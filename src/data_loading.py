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


def cargar_crudo(ruta: Path | str | None = None) -> pd.DataFrame:
    """Lee el archivo original sin transformar.

    Si no se entrega una ruta, se usa la ruta por defecto definida en config.
    Lanza FileNotFoundError con un mensaje claro cuando el archivo no existe,
    para orientar a quien ejecuta el proyecto por primera vez.
    """
    ruta = Path(ruta) if ruta is not None else config.RUTA_DATOS_RAW
    if not Path(ruta).exists():
        raise FileNotFoundError(
            f"No se encontro el archivo de datos en: {ruta}\n"
            "Descargue games.csv desde Kaggle o Hugging Face y coloquelo en "
            "data/raw/ (ver instrucciones en el README)."
        )
    # low_memory=False evita advertencias de tipos mixtos en columnas de texto
    return pd.read_csv(ruta, low_memory=False)


def _contar_idiomas(valor) -> float:
    """Cuenta cuantos idiomas soporta un juego a partir del campo de texto.

    El campo suele venir como una lista en formato texto, por ejemplo
    "['English', 'French', 'Spanish - Spain']". Se intenta interpretar como
    lista; si falla, se recurre a un conteo por comas. Devuelve NaN cuando el
    valor esta vacio o no es interpretable.
    """
    if pd.isna(valor):
        return np.nan
    texto = str(valor).strip()
    if texto == "" or texto == "[]":
        return np.nan
    try:
        elementos = ast.literal_eval(texto)
        if isinstance(elementos, (list, tuple)):
            return float(len([e for e in elementos if str(e).strip() != ""]))
    except (ValueError, SyntaxError):
        pass
    # Respaldo: conteo por comas
    return float(len([p for p in texto.split(",") if p.strip() != ""]))


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
        fecha = pd.to_datetime(df[cols["fecha_lanzamiento"]], errors="coerce")
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
        datos["n_idiomas"] = df[cols["idiomas"]].map(_contar_idiomas)

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
            labels=["Gratis", "Menos de 5", "5 a 15", "15 a 30", "Mas de 30"],
        )

    # Indicadores derivados finales
    if "pct_positivas" in datos.columns:
        datos["bien_recibido"] = datos["pct_positivas"] >= config.UMBRAL_BIEN_RECIBIDO
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
    desc = desc.rename(columns={
        "count": "conteo", "mean": "media", "std": "desv_est",
        "min": "minimo", "25%": "p25", "50%": "mediana",
        "75%": "p75", "max": "maximo",
    })
    return desc.round(3)
