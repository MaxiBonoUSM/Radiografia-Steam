"""
Pagina 2: Analisis Exploratorio.

Proposito analitico: responder "como se comportan nuestros datos".
Concentra el analisis univariado y las primeras comparaciones entre grupos:
distribucion de la variable objetivo, distribucion de precios, frecuencia de
generos y recepcion comparada por genero. Incluye estadisticas descriptivas.

Las interpretaciones se calculan a partir de los datos filtrados, de modo que
el texto siempre describe lo que muestra el grafico en pantalla.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _shared import (  # noqa: E402
    encabezado, obtener_datos, aplicar_filtros, grafico, interpretacion, pct, num, dec,
)
from src import data_loading, viz  # noqa: E402

encabezado("2. Análisis Exploratorio", "¿Cómo se comportan nuestros datos?")

datos = obtener_datos()
if datos is None:
    st.stop()

datos_f = aplicar_filtros(datos)
if datos_f.empty:
    st.warning("Los filtros actuales no dejan juegos. Amplíe los rangos del panel lateral.")
    st.stop()

# Analisis univariado
st.subheader("Análisis univariado")

col_a, col_b = st.columns(2)
with col_a:
    grafico(viz.distribucion_y(datos_f))
    y = datos_f["pct_positivas"].dropna()
    interpretacion(
        f"La mediana de reseñas positivas es {pct(y.median())} y el "
        f"{pct((y >= 0.8).mean())} de los juegos supera el 80 %. La distribución "
        "está cargada hacia valores altos, con una cola larga de juegos mal "
        "recibidos: el interés analítico está en qué características acompañan a esa cola."
    )
with col_b:
    log_y = st.toggle("Eje vertical logarítmico", value=True,
                      help="Útil porque los precios están muy sesgados hacia valores bajos.")
    grafico(viz.distribucion_precio(datos_f, log_y=log_y))
    p = datos_f["precio"]
    interpretacion(
        f"El precio mediano es {dec(p.median())} USD, el {pct((p == 0).mean())} de los "
        f"juegos es gratuito y el 75 % cuesta {dec(p.quantile(0.75))} USD o menos. "
        f"Solo {num((p > 100).sum())} juegos superan los 100 USD (máximo "
        f"{dec(p.max())} USD). La vista parte en el percentil 99; con doble clic sobre "
        "el gráfico se ve el rango completo."
    )

frec = viz.explotar_generos(datos_f)["genero"].value_counts()
n_generos = st.slider(
    "Géneros a mostrar", 5, max(5, len(frec)), min(12, max(5, len(frec))),
    help=f"El catálogo filtrado tiene {len(frec)} géneros distintos. Incluye categorías "
         "de software (Utilities, Animation & Modeling) que aparecen al ampliar la lista.",
)
grafico(viz.frecuencia_generos(datos_f, top=n_generos))
if len(frec) >= 3:
    interpretacion(
        f"{frec.index[0]} es el género más declarado ({num(frec.iloc[0])} juegos), "
        f"seguido de {frec.index[1]} ({num(frec.iloc[1])}) y {frec.index[2]} "
        f"({num(frec.iloc[2])}). Un juego puede declarar varios géneros, por lo que "
        "las barras no suman el total de juegos."
    )

st.divider()

# Comparacion entre grupos
st.subheader("Comparación entre grupos")
grafico(viz.recepcion_por_genero(datos_f, top=n_generos))
g = viz.explotar_generos(datos_f.dropna(subset=["pct_positivas"]))
top = g["genero"].value_counts().head(n_generos).index
med = g[g["genero"].isin(top)].groupby("genero")["pct_positivas"].median().sort_values()
if len(med) >= 2:
    interpretacion(
        f"Entre los {len(med)} géneros con más juegos, {med.index[-1]} tiene la mediana más "
        f"alta ({pct(med.iloc[-1])}) y {med.index[0]} la más baja ({pct(med.iloc[0])}). "
        f"La brecha es de {abs(med.iloc[-1] - med.iloc[0]) * 100:.0f} puntos: el género "
        "se asocia a la recepción, pero las cajas se traslapan mucho, así que por sí "
        "solo no la determina."
    )

st.divider()

# Estadisticas descriptivas
st.subheader("Estadísticas descriptivas")
st.dataframe(
    data_loading.estadisticas_descriptivas(datos_f),
    use_container_width=True,
)
st.caption(
    "Las estadísticas respaldan las observaciones anteriores. Destaca la fuerte "
    "asimetría del total de reseñas: la media es muy superior a la mediana porque "
    "unos pocos juegos concentran la mayor parte de las reseñas. El tiempo de juego "
    "tiene mediana 0 porque la fuente no lo registra para la mayoría de los juegos."
)
