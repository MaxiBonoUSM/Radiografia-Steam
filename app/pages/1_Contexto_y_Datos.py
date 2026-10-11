"""
Pagina 1: Contexto y Datos.

Proposito analitico: responder "que estamos estudiando y con que datos".
Presenta indicadores generales del dataset y, sobre todo, su estructura y
calidad: numero de observaciones, variables, tipos, valores faltantes y
cobertura temporal. Deja explicito que problemas se encontraron en los datos.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _shared import encabezado, obtener_datos, aplicar_filtros, COLORES  # noqa: E402
from src import config, data_loading, viz  # noqa: E402

st.set_page_config(page_title="Contexto y Datos", page_icon="chart", layout="wide")

encabezado("1. Contexto y Datos", "Que estamos estudiando y con que datos")

datos = obtener_datos()
if datos is None:
    st.stop()

datos_f = aplicar_filtros(datos)

# Indicadores generales
st.subheader("Indicadores generales")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Juegos (filtrados)", f"{len(datos_f):,}".replace(",", "."))
if "anio" in datos_f:
    c2.metric("Periodo", f"{int(datos_f['anio'].min())} a {int(datos_f['anio'].max())}")
if "pct_positivas" in datos_f:
    med = datos_f["pct_positivas"].median()
    c3.metric("Mediana de resenas positivas", f"{med:.0%}" if med == med else "s/d")
if "bien_recibido" in datos_f:
    tasa = datos_f["bien_recibido"].mean()
    c4.metric("Juegos bien recibidos", f"{tasa:.0%}" if tasa == tasa else "s/d",
              help=f"Al menos {config.UMBRAL_BIEN_RECIBIDO:.0%} de resenas positivas")

st.divider()

# Estructura y calidad de los datos
st.subheader("Estructura y calidad de los datos")
st.markdown(
    """
El dataset trae un juego por fila. Antes de analizar, se revisaron los problemas
tipicos de calidad. Las decisiones de limpieza aplicadas fueron:

- **Cobertura temporal:** se parseo la fecha de lanzamiento y se acoto la ventana
  a 2014 a 2024. Las fechas no interpretables se marcaron como faltantes.
- **Indicador de recepcion:** se construyo la proporcion de resenas positivas
  como positivas sobre el total. Es indefinida cuando el juego no tiene resenas.
- **Umbral de resenas:** la proporcion es poco confiable con muy pocas resenas,
  por lo que se agrego un umbral minimo ajustable desde el panel lateral.
- **Campos de multiples valores:** generos, categorias e idiomas se procesaron
  para extraer el genero principal, las funcionalidades comunitarias y el conteo
  de idiomas.
"""
)

try:
    calidad = data_loading.resumen_calidad(
        data_loading.cargar_crudo(config.RUTA_DATOS_RAW)
    )
    st.markdown("**Valores faltantes por columna (archivo original)**")
    st.dataframe(calidad, use_container_width=True, height=320)
except FileNotFoundError:
    st.caption(
        "El resumen de calidad por columna del archivo original se muestra cuando "
        "los datos se cargan desde data/raw. Con un archivo subido se omite para no "
        "releer el archivo completo."
    )

st.divider()

# Contexto temporal
st.subheader("Contexto temporal del catalogo")
st.plotly_chart(viz.releases_por_anio(datos_f), use_container_width=True)
st.markdown(
    f"<p style='color:{COLORES['gris']}'>El volumen de lanzamientos permite dimensionar "
    "la saturacion del mercado dentro del periodo analizado.</p>",
    unsafe_allow_html=True,
)
