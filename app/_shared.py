"""
Utilidades compartidas por las paginas de la aplicacion Streamlit.

Centraliza tres cosas que todas las paginas necesitan: la carga de datos con
cache, los filtros interactivos del panel lateral y un pequenio encabezado comun.
Mantener esto en un solo lugar asegura coherencia visual y evita repetir codigo.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

# Permite importar el paquete src cuando Streamlit ejecuta las paginas
RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src import config, data_loading  # noqa: E402

COLORES = config.COLORES


@st.cache_data(show_spinner="Cargando y limpiando el dataset...")
def _cargar_desde_ruta(ruta: str, min_resenas: int):
    crudo = data_loading.cargar_crudo(ruta)
    limpio = data_loading.limpiar(crudo, min_resenas=min_resenas)
    return limpio, data_loading.resumen_calidad(crudo), len(crudo)


@st.cache_data(show_spinner="Limpiando el dataset subido...")
def _cargar_desde_subida(contenido, min_resenas: int):
    crudo = data_loading.cargar_crudo(contenido)
    limpio = data_loading.limpiar(crudo, min_resenas=min_resenas)
    return limpio, data_loading.resumen_calidad(crudo), len(crudo)


def obtener_calidad():
    """Devuelve (tabla de calidad, filas del archivo original) de la ultima carga."""
    return st.session_state.get("calidad"), st.session_state.get("filas_crudo")


def obtener_datos() -> pd.DataFrame | None:
    """Carga el dataset segun la fuente elegida en el panel lateral.

    Admite dos fuentes: la ruta por defecto data/raw/games.csv o un archivo CSV
    subido por el usuario. Devuelve None si todavia no hay datos disponibles, y
    deja un mensaje de ayuda en pantalla.
    """
    st.sidebar.header("Fuente de datos")
    fuente = st.sidebar.radio(
        "Origen del archivo",
        ["Ruta del proyecto (data/raw)", "Subir archivo CSV"],
        help="Por defecto se busca data/raw/games.csv. También puede subir el CSV.",
    )

    if fuente == "Subir archivo CSV":
        archivo = st.sidebar.file_uploader("Seleccione games.csv", type=["csv"])
        if archivo is None:
            st.info("Suba el archivo games.csv para comenzar.")
            return None
        try:
            limpio, calidad, filas = _cargar_desde_subida(archivo, config.MIN_RESENAS_DEFECTO)
        except Exception as exc:
            st.error(f"No fue posible leer el archivo subido: {exc}")
            return None
    else:
        ruta = str(config.RUTA_DATOS_RAW)
        try:
            limpio, calidad, filas = _cargar_desde_ruta(ruta, config.MIN_RESENAS_DEFECTO)
        except FileNotFoundError as exc:
            st.warning(str(exc))
            st.info("Como alternativa, cambie la fuente a 'Subir archivo CSV' en el panel lateral.")
            return None

    st.session_state["calidad"] = calidad
    st.session_state["filas_crudo"] = filas
    if limpio.empty:
        st.error(
            "La limpieza dejó 0 juegos en la ventana 2014 a 2024. Revise que el "
            "archivo sea el games.csv original y que la columna de fecha tenga el "
            "formato 'Aug 1, 2023'."
        )
        return None
    return limpio


def aplicar_filtros(df: pd.DataFrame) -> pd.DataFrame:
    """Dibuja los controles del panel lateral y devuelve el DataFrame filtrado.

    Estos controles son el nucleo interactivo de la aplicacion: modifican de
    forma significativa todas las visualizaciones de las paginas. Incluyen el
    rango de anios, el umbral minimo de resenas, el rango de precio y la
    seleccion de generos.
    """
    st.sidebar.header("Filtros")

    anio_min, anio_max = int(df["anio"].min()), int(df["anio"].max())
    rango_anios = st.sidebar.slider(
        "Año de lanzamiento", anio_min, anio_max, (anio_min, anio_max),
        help="Acota la ventana temporal del análisis.",
    )

    min_resenas = st.sidebar.slider(
        "Mínimo de reseñas", 0, 500, config.MIN_RESENAS_DEFECTO, step=5,
        help="Por defecto no se excluye ningún juego. Los análisis de recepción usan "
             "solo juegos con al menos una reseña. Subir el mínimo (por ejemplo a "
             f"{config.MIN_RESENAS_ROBUSTEZ}) permite comprobar si los hallazgos se "
             "mantienen con proporciones más estables.",
    )

    precio_max = float(np.ceil(df["precio"].max())) if "precio" in df else 1000.0
    rango_precio = st.sidebar.slider(
        "Rango de precio (USD)", 0.0, precio_max, (0.0, precio_max), step=1.0,
        help="Por defecto incluye todos los precios, hasta el máximo del catálogo.",
    )

    generos_disp = sorted(
        {g.strip() for lista in df["generos"].dropna() for g in lista.split(",") if g.strip()}
    ) if "generos" in df else []
    generos_sel = st.sidebar.multiselect(
        "Géneros", generos_disp, default=[],
        help="Incluye los juegos que declaran al menos uno de los géneros elegidos. "
             "Vacío significa todos.",
    )

    f = df.copy()
    f = f[f["anio"].between(*rango_anios)]
    if "total_resenas" in f:
        f = f[f["total_resenas"] >= min_resenas]
    if "precio" in f:
        f = f[f["precio"].between(*rango_precio)]
    if generos_sel:
        listas = f["generos"].fillna("").str.split(",").map(
            lambda gs: {g.strip() for g in gs}
        )
        f = f[listas.map(lambda gs: bool(gs & set(generos_sel)))]

    st.sidebar.caption(f"Juegos tras aplicar filtros: {len(f):,}".replace(",", "."))
    return f


def grafico(fig, **_) -> None:
    """Dibuja una figura de Plotly respetando su estilo propio.

    Con theme=None, Streamlit no reemplaza los colores de la figura. Esto evita
    que, en modo oscuro, los titulos de los ejes queden con un color parecido al
    del fondo: cada figura conserva su fondo blanco y sus textos oscuros.
    """
    st.plotly_chart(fig, use_container_width=True, theme=None)


def encabezado(titulo: str, subtitulo: str) -> None:
    """Dibuja un encabezado consistente en cada pagina.

    El titulo no fija un color propio: hereda el color de texto del tema, de modo
    que se lee bien tanto en modo claro como en modo oscuro.
    """
    st.markdown(
        f"<h1 style='margin-bottom:0'>{titulo}</h1>"
        f"<p style='opacity:0.75;font-size:1.05rem;margin-top:4px'>{subtitulo}</p>"
        f"<hr style='border:none;border-top:2px solid {COLORES['steam']};margin-top:6px'>",
        unsafe_allow_html=True,
    )


def interpretacion(texto: str) -> None:
    """Muestra la interpretacion de un grafico bajo este (Observacion e Interpretacion)."""
    st.markdown(f"**Interpretación.** {texto}")


def pct(valor: float) -> str:
    """Formatea una proporcion como porcentaje entero (0.808 se muestra como 81 %)."""
    return "s/d" if pd.isna(valor) else f"{valor * 100:.0f} %"


def num(valor: float) -> str:
    """Formatea un entero con punto como separador de miles."""
    return f"{int(valor):,}".replace(",", ".")


def dec(valor: float, decimales: int = 2, signo: bool = False) -> str:
    """Formatea un decimal con coma, como se usa en Chile (2.79 se muestra 2,79)."""
    if pd.isna(valor):
        return "s/d"
    valor = round(float(valor), decimales) + 0.0  # evita mostrar "-0,00"
    formato = f"{{:{'+' if signo else ''}.{decimales}f}}"
    return formato.format(valor).replace(".", ",")
