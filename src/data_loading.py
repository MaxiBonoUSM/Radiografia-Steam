"""
Carga y limpieza del dataset de Steam.

Este modulo concentra todo el proceso de preparacion de datos descrito en el
Avance 2: lectura del archivo original, normalizacion de nombres de columna,
parseo de fechas, construccion de indicadores derivados (proporcion de resenas
positivas, numero de idiomas, funcionalidades comunitarias) y filtrado por la
ventana temporal del proyecto.

Las funciones no dependen de Streamlit, de modo que pueden usarse tanto desde el
notebook de EDA como desde la aplicacion. La aplicacion envuelve estas funciones
con su propia capa de cache.
"""

from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pandas as pd

from . import config


def resolver_columnas(df: pd.DataFrame) -> dict:
    """Devuelve un diccionario {nombre_canonico: nombre_real} segun el archivo.

    Recorre el resolvedor de alias de la configuracion y, para cada nombre
    canonico, busca la primera variante presente en el DataFrame. Las columnas
    que no aparecen simplemente se omiten, de modo que el pipeline sigue
    funcionando aunque el archivo de origen no traiga todos los campos.
    """
    mapa = {}
    for canonico, posibles in config.ALIAS_COLUMNAS.items():
        for candidato in posibles:
            if candidato in df.columns:
                mapa[canonico] = candidato
                break
    return mapa


# Columnas de texto extenso o de enlaces que no aportan a la pregunta. Se omiten
# al leer para reducir el uso de memoria (el archivo completo pesa cerca de 400 MB).
COLUMNAS_OMITIDAS = {
    "About the game", "detailed_description", "short_description", "Reviews",
    "reviews", "Header image", "header_image", "Website", "website",
    "Support url", "support_url", "Support email", "support_email",
    "Metacritic url", "metacritic_url", "Notes", "notes", "Screenshots",
    "screenshots", "Movies", "movies",
}


def _corregir_encabezado(nombres: list[str]) -> list[str]:
    """Corrige el error conocido del encabezado del CSV de Fronkon Games.

    En el archivo original las columnas "Discount" y "DLC count" aparecen
    fusionadas en un solo nombre ("DiscountDLC count"). Por eso el encabezado
    tiene un nombre menos que los valores de cada fila, y pandas desplaza todas
    las columnas una posicion (el AppID termina como indice y, por ejemplo, la
    columna de fecha queda con los tramos de propietarios). Se separa el nombre
    fusionado para que encabezado y valores vuelvan a coincidir.
    """
    corregidos = []
    for nombre in nombres:
        if nombre == "DiscountDLC count":
            corregidos.extend(["Discount", "DLC count"])
        else:
            corregidos.append(nombre)
    return corregidos


def cargar_crudo(fuente=None, solo_utiles: bool = True) -> pd.DataFrame:
    """Lee el archivo original corrigiendo su encabezado.

    La fuente puede ser una ruta o un archivo ya abierto (por ejemplo, el CSV
    subido desde la aplicacion). Si no se entrega fuente, se usa la ruta por
    defecto definida en config. Con solo_utiles=True se omiten las columnas de
    texto extenso para ahorrar memoria.

    Lanza FileNotFoundError con un mensaje claro cuando el archivo no existe,
    para orientar a quien ejecuta el proyecto por primera vez.
    """
    if fuente is None:
        fuente = config.RUTA_DATOS_RAW
    es_ruta = isinstance(fuente, (str, Path))
    if es_ruta and not Path(fuente).exists():
        raise FileNotFoundError(
            f"No se encontro el archivo de datos en: {fuente}\n"
            "Descargue games.csv desde Kaggle o Hugging Face y coloquelo en "
            "data/raw/ (ver instrucciones en el README)."
        )

    # Lectura previa del encabezado para detectar y corregir el desfase
    encabezado = pd.read_csv(fuente, nrows=0).columns.tolist()
    if not es_ruta and hasattr(fuente, "seek"):
        fuente.seek(0)
    nombres = _corregir_encabezado(encabezado)

    usar = [n for n in nombres if not (solo_utiles and n in COLUMNAS_OMITIDAS)]

    # header=0 descarta la linea original y names aplica el encabezado corregido.
    # index_col=False impide que pandas use la primera columna como indice.
    # low_memory=False evita advertencias de tipos mixtos en columnas de texto.
    return pd.read_csv(
        fuente, header=0, names=nombres, usecols=usar,
        index_col=False, low_memory=False,
    )


def _parsear_fechas(serie: pd.Series) -> pd.Series:
    """Convierte la fecha de lanzamiento a datetime.

    El formato habitual del dataset es "Aug 1, 2023". Se intenta primero ese
    formato y, para las filas que no calzan (por ejemplo "Aug 2023"), se usa una
    interpretacion flexible. Las fechas imposibles de leer quedan como NaT.
    """
    texto = serie.astype("string").str.strip()
    fecha = pd.to_datetime(texto, format="%b %d, %Y", errors="coerce")
    faltan = fecha.isna() & texto.notna()
    if faltan.any():
        fecha.loc[faltan] = pd.to_datetime(
            texto[faltan], format="mixed", errors="coerce"
        )
    return fecha


def _lista_idiomas(valor) -> list[str]:
    """Convierte el campo de idiomas en una lista de nombres.

    El campo suele venir como una lista en formato texto, por ejemplo
    "['English', 'French', 'Spanish - Spain']". Se intenta interpretar como
    lista de Python; si falla (algunos nombres traen apostrofes, como K'iche),
    se separa por comas y se quitan las comillas. Ningun nombre de idioma de
    Steam contiene comas, por lo que este respaldo es seguro. Devuelve una lista
    vacia cuando el valor esta vacio.
    """
    if pd.isna(valor):
        return []
    texto = str(valor).strip()
    if texto in ("", "[]"):
        return []
    try:
        elementos = ast.literal_eval(texto)
        if isinstance(elementos, (list, tuple)):
            return [str(e).strip() for e in elementos if str(e).strip()]
    except (ValueError, SyntaxError):
        pass
    interior = texto.strip("[]")
    return [p.strip().strip("'\"") for p in interior.split(",") if p.strip()]


def _contar_idiomas(valor) -> float:
    """Cuenta cuantos idiomas soporta un juego. Devuelve NaN si no declara ninguno."""
    n = len(_lista_idiomas(valor))
    return float(n) if n > 0 else np.nan


def _a_booleano(serie: pd.Series) -> pd.Series:
    """Convierte una columna de soporte de sistema operativo a booleano."""
    return (
        serie.astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "yes", "si"])
    )


def _contiene(serie: pd.Series, termino: str) -> pd.Series:
    """Indica si un campo de texto separado por comas contiene cierto termino."""
    return serie.fillna("").astype(str).str.contains(termino, case=False, regex=False)


def limpiar(df: pd.DataFrame, min_resenas: int | None = None) -> pd.DataFrame:
    """Aplica todo el proceso de limpieza y devuelve un DataFrame analitico.

    Pasos principales:
      1. Normaliza nombres de columna con el resolvedor.
      2. Convierte precio, resenas y tiempos de juego a numerico.
      3. Parsea la fecha de lanzamiento y extrae anio y mes.
      4. Filtra la ventana 2014 a 2024.
      5. Construye indicadores derivados.
      6. Marca, sin eliminar, los juegos bajo el umbral minimo de resenas.

    El parametro min_resenas solo define el valor de la columna indicadora
    'sobre_umbral'; no elimina filas, para que la aplicacion pueda filtrar de
    forma interactiva.
    """
    if min_resenas is None:
        min_resenas = config.MIN_RESENAS_DEFECTO

    cols = resolver_columnas(df)
    datos = pd.DataFrame(index=df.index)

    # Identificacion y nombre
    if "app_id" in cols:
        datos["app_id"] = df[cols["app_id"]]
    if "nombre" in cols:
        datos["nombre"] = df[cols["nombre"]]

    # Variables numericas base
    for clave in ["precio", "positivas", "negativas", "playtime_mediano",
                  "playtime_medio", "peak_ccu", "dlc_count", "recomendaciones",
                  "metacritic"]:
        if clave in cols:
            datos[clave] = pd.to_numeric(df[cols[clave]], errors="coerce")

    # Fecha de lanzamiento, anio y mes
    if "fecha_lanzamiento" in cols:
        fecha = _parsear_fechas(df[cols["fecha_lanzamiento"]])
        datos["fecha_lanzamiento"] = fecha
        datos["anio"] = fecha.dt.year
        datos["mes"] = fecha.dt.month

    # Indicadores de recepcion
    if {"positivas", "negativas"}.issubset(datos.columns):
        datos["total_resenas"] = datos["positivas"].fillna(0) + datos["negativas"].fillna(0)
        total = datos["total_resenas"].replace(0, np.nan)
        datos["pct_positivas"] = datos["positivas"] / total

    # Numero de idiomas
    if "idiomas" in cols:
        datos["lista_idiomas"] = df[cols["idiomas"]].map(_lista_idiomas)
        n = datos["lista_idiomas"].map(len).astype(float)
        datos["n_idiomas"] = n.where(n > 0)
        # Declaraciones implausibles (todos los idiomas de la tienda marcados en
        # bloque). No se eliminan: se identifican para mostrarlas aparte.
        datos["idiomas_atipico"] = datos["n_idiomas"] > config.MAX_IDIOMAS_PLAUSIBLE

    # Soporte de sistemas operativos
    n_os = pd.Series(0, index=df.index)
    for so in ["windows", "mac", "linux"]:
        if so in cols:
            datos[so] = _a_booleano(df[cols[so]])
            n_os = n_os + datos[so].astype(int)
    datos["n_sistemas"] = n_os
    datos["multiplataforma"] = n_os >= 2

    # Funcionalidades comunitarias (a partir de Categories)
    if "categorias" in cols:
        datos["multijugador"] = _contiene(df[cols["categorias"]], "Multi-player")
        datos["steam_workshop"] = _contiene(df[cols["categorias"]], "Steam Workshop")
        datos["comunidad"] = datos["multijugador"] | datos["steam_workshop"]

    # Genero principal (primer genero listado)
    if "generos" in cols:
        datos["generos"] = df[cols["generos"]].fillna("").astype(str)
        # Numero de generos declarados (sirve como senal de metadatos inflados)
        n_gen = datos["generos"].str.split(",").map(
            lambda lista: len([g for g in lista if g.strip()])
        )
        datos["n_generos"] = n_gen.where(n_gen > 0)
        datos["genero_principal"] = (
            datos["generos"].str.split(",").str[0].str.strip().replace("", np.nan)
        )

    # Duenos estimados (tramo textual, se conserva como categoria)
    if "duenos_estimados" in cols:
        datos["duenos_estimados"] = df[cols["duenos_estimados"]]

    # Filtro de ventana temporal del proyecto
    if "anio" in datos.columns:
        datos = datos[datos["anio"].between(config.ANIO_INICIO, config.ANIO_FIN)]

    # Tramo de precio (categorico legible)
    if "precio" in datos.columns:
        datos["tramo_precio"] = pd.cut(
            datos["precio"],
            bins=[-0.01, 0.0, 4.99, 14.99, 29.99, np.inf],
            labels=["Gratis", "Menos de 5", "5 a 15", "15 a 30", "Más de 30"],
        )

    # Indicadores derivados finales
    if "pct_positivas" in datos.columns:
        # Queda vacio (NaN) cuando el juego no tiene resenas, para que los
        # porcentajes se calculen solo sobre juegos que si pueden evaluarse.
        datos["bien_recibido"] = (
            datos["pct_positivas"] >= config.UMBRAL_BIEN_RECIBIDO
        ).astype(float).where(datos["pct_positivas"].notna())
    if "total_resenas" in datos.columns:
        datos["sobre_umbral"] = datos["total_resenas"] >= min_resenas

    return datos.reset_index(drop=True)


def resumen_calidad(df_crudo: pd.DataFrame) -> pd.DataFrame:
    """Construye una tabla de calidad por columna del archivo original.

    Devuelve, para cada columna, su tipo, el conteo de no nulos, el conteo y el
    porcentaje de nulos. Sirve para la pagina de contexto y calidad de datos.
    """
    resumen = pd.DataFrame({
        "columna": df_crudo.columns,
        "tipo": [str(t) for t in df_crudo.dtypes],
        "no_nulos": df_crudo.notna().sum().values,
        "nulos": df_crudo.isna().sum().values,
    })
    resumen["pct_nulos"] = (resumen["nulos"] / len(df_crudo) * 100).round(1)
    return resumen.sort_values("pct_nulos", ascending=False).reset_index(drop=True)


def estadisticas_descriptivas(df: pd.DataFrame) -> pd.DataFrame:
    """Entrega estadisticas descriptivas de las variables numericas clave."""
    columnas = [c for c in ["pct_positivas", "precio", "total_resenas",
                            "n_idiomas", "playtime_mediano"] if c in df.columns]
    desc = df[columnas].describe(percentiles=[0.25, 0.5, 0.75]).T
    desc.index = [config.ETIQUETAS.get(c, c) for c in desc.index]
    desc = desc.rename(columns={
        "count": "Conteo", "mean": "Media", "std": "Desv. estándar",
        "min": "Mínimo", "25%": "P25", "50%": "Mediana",
        "75%": "P75", "max": "Máximo",
    })
    return desc.round(3)


def chequeos_calidad(df_crudo: pd.DataFrame) -> dict:
    """Verificaciones de calidad sobre el archivo original.

    Revisa duplicados (por AppID y por filas completas), nombres repetidos entre
    juegos distintos, valores imposibles (precios o resenas negativos) y el rango
    de fechas. Devuelve un diccionario con los conteos, usado en la pagina de
    contexto y calidad.
    """
    cols = resolver_columnas(df_crudo)
    res = {"filas": len(df_crudo), "columnas": df_crudo.shape[1]}
    if "app_id" in cols:
        res["appid_duplicados"] = int(df_crudo[cols["app_id"]].duplicated().sum())
    res["filas_identicas"] = int(df_crudo.duplicated().sum())
    if "nombre" in cols:
        nombres = df_crudo[cols["nombre"]]
        repetidos = nombres[nombres.duplicated(keep=False) & nombres.notna()]
        res["juegos_nombre_compartido"] = int(len(repetidos))
        res["nombres_compartidos"] = int(repetidos.nunique())
    negativos = 0
    for clave in ("precio", "positivas", "negativas"):
        if clave in cols:
            negativos += int((pd.to_numeric(df_crudo[cols[clave]], errors="coerce") < 0).sum())
    res["valores_negativos"] = negativos
    if "fecha_lanzamiento" in cols:
        anios = _parsear_fechas(df_crudo[cols["fecha_lanzamiento"]]).dt.year
        res["anio_min"] = int(anios.min())
        res["anio_max"] = int(anios.max())
        res["fechas_invalidas"] = int(anios.isna().sum())
    return res
