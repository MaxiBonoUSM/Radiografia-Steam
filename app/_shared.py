"""
Utilidades compartidas por las paginas de la aplicacion Streamlit.

Centraliza tres cosas que todas las paginas necesitan: la carga de datos con
cache, los filtros interactivos del panel lateral y un pequenio encabezado comun.
Mantener esto en un solo lugar asegura coherencia visual y evita repetir codigo.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Permite importar el paquete src cuando Streamlit ejecuta las paginas
RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src import config, data_loading  # noqa: E402

COLORES = config.COLORES


@st.cache_data(show_spinner="Cargando y limpiando el dataset...")
def _cargar_desde_ruta(ruta: str, min_resenas: int) -> pd.DataFrame:
    crudo = data_loading.cargar_crudo(ruta)
    return data_loading.limpiar(crudo, min_resenas=min_resenas)


@st.cache_data(show_spinner="Limpiando el dataset subido...")
def _cargar_desde_subida(contenido, min_resenas: int) -> pd.DataFrame:
    crudo = pd.read_csv(contenido, low_memory=False)
    return data_loading.limpiar(crudo, min_resenas=min_resenas)


@st.cache_data(show_spinner=False)
def _calidad_desde_ruta(ruta: str) -> pd.DataFrame:
    crudo = data_loading.cargar_crudo(ruta)
    return data_loading.resumen_calidad(crudo)


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
        help="Por defecto se busca data/raw/games.csv. Tambien puede subir el CSV.",
    )

    if fuente == "Subir archivo CSV":
        archivo = st.sidebar.file_uploader("Seleccione games.csv", type=["csv"])
        if archivo is None:
            st.info("Suba el archivo games.csv para comenzar.")
            return None
        try:
            return _cargar_desde_subida(archivo, config.MIN_RESENAS_DEFECTO)
        except Exception as exc:
            st.error(f"No fue posible leer el archivo subido: {exc}")
            return None

    ruta = str(config.RUTA_DATOS_RAW)
    try:
        return _cargar_desde_ruta(ruta, config.MIN_RESENAS_DEFECTO)
    except FileNotFoundError as exc:
        st.warning(str(exc))
        st.info("Como alternativa, cambie la fuente a 'Subir archivo CSV' en el panel lateral.")
        return None


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
        "Anio de lanzamiento", anio_min, anio_max, (anio_min, anio_max),
        help="Acota la ventana temporal del analisis.",
    )

    min_resenas = st.sidebar.slider(
        "Minimo de resenas", 0, 500, config.MIN_RESENAS_DEFECTO, step=10,
        help="La proporcion de positivas es poco confiable con pocas resenas.",
    )

    precio_max = float(min(df["precio"].max() if "precio" in df else 100, 100))
    rango_precio = st.sidebar.slider(
        "Rango de precio (USD)", 0.0, precio_max, (0.0, precio_max),
    )

    generos_disp = sorted(df["genero_principal"].dropna().unique().tolist()) \
        if "genero_principal" in df else []
    generos_sel = st.sidebar.multiselect(
        "Generos principales", generos_disp, default=[],
        help="Vacio significa todos los generos.",
    )

    f = df.copy()
    f = f[f["anio"].between(*rango_anios)]
    if "total_resenas" in f:
        f = f[f["total_resenas"] >= min_resenas]
    if "precio" in f:
        f = f[f["precio"].between(*rango_precio)]
    if generos_sel:
        f = f[f["genero_principal"].isin(generos_sel)]

    st.sidebar.caption(f"Juegos tras aplicar filtros: {len(f):,}".replace(",", "."))
    return f


def encabezado(titulo: str, subtitulo: str) -> None:
    """Dibuja un encabezado consistente en cada pagina."""
    st.markdown(
        f"<h1 style='color:{COLORES['navy']};margin-bottom:0'>{titulo}</h1>"
        f"<p style='color:{COLORES['gris']};font-size:1.05rem;margin-top:4px'>{subtitulo}</p>"
        f"<hr style='border:none;border-top:2px solid {COLORES['steam']};margin-top:6px'>",
        unsafe_allow_html=True,
    )
