"""
Pagina 3: Analisis de la Pregunta.

Proposito analitico: responder "que hemos aprendido hasta ahora sobre nuestra
pregunta". Conecta el EDA con la problematica: estudia relaciones entre los
predictores X y el objetivo Y, el componente temporal T y resume los hallazgos
preliminares.

Las interpretaciones se calculan a partir de los datos filtrados, de modo que
el texto siempre describe lo que muestra el grafico en pantalla.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _shared import (  # noqa: E402
    encabezado, obtener_datos, aplicar_filtros, grafico, interpretacion, pct, dec, num,
)
from src import viz  # noqa: E402

encabezado("3. Análisis de la Pregunta", "¿Qué hemos aprendido hasta ahora?")

datos = obtener_datos()
if datos is None:
    st.stop()

datos_f = aplicar_filtros(datos)
if len(datos_f) < 30:
    st.warning("Los filtros actuales dejan muy pocos juegos para analizar relaciones. "
               "Amplíe los rangos del panel lateral.")
    st.stop()

con_y = datos_f.dropna(subset=["pct_positivas"])


def _spearman(col: str) -> float:
    return con_y[col].corr(con_y["pct_positivas"], method="spearman")


# Relacion entre X e Y
st.subheader("Relaciones entre características (X) y recepción (Y)")

col_a, col_b = st.columns(2)
with col_a:
    tendencia = st.toggle("Mostrar mediana por tramo de precio", value=True)
    grafico(viz.precio_vs_recepcion(datos_f, con_tendencia=tendencia))
with col_b:
    grafico(viz.recepcion_por_tramo_precio(datos_f))
tramos = viz.mediana_por_tramo_precio(con_y).set_index("tramo")
if len(tramos) >= 2:
    mejor, peor = tramos["pct_positivas"].idxmax(), tramos["pct_positivas"].idxmin()
    interpretacion(
        f"La relación entre precio y recepción es débil (Spearman "
        f"{dec(_spearman('precio'))}) y no lineal. La dispersión muestra los juegos "
        "individuales (su vista inicial llega al percentil 99 de precio; con doble clic "
        "se ve el rango completo) y el gráfico de la derecha resume cada tramo: la "
        f"mediana más alta está en «{mejor}» USD ({pct(tramos.loc[mejor, 'pct_positivas'])}) "
        f"y la más baja en «{peor}» USD ({pct(tramos.loc[peor, 'pct_positivas'])}, "
        f"{num(tramos.loc[peor, 'juegos'])} juegos). Cobrar más no garantiza una mejor "
        "valoración; sobre los 40 USD la recepción cae con claridad."
    )

col_c, col_d = st.columns(2)
with col_c:
    grafico(viz.recepcion_por_comunidad(datos_f))
    grupos = con_y.groupby("comunidad")["pct_positivas"].median()
    if {True, False}.issubset(grupos.index):
        dif = (grupos[True] - grupos[False]) * 100
        sentido = "levemente peor" if dif < 0 else "levemente mejor"
        interpretacion(
            f"Los juegos con multijugador o Steam Workshop se valoran {sentido} "
            f"({pct(grupos[True])} frente a {pct(grupos[False])}, {dec(dif, 1, signo=True)} "
            "puntos). Contra lo esperado, la comunidad no se asocia a mejor recepción; una "
            "hipótesis es que el multijugador expone el juego a más críticas (servidores, "
            "emparejamiento, comunidad activa)."
        )
with col_d:
    grafico(viz.idiomas_vs_popularidad(datos_f))
    pop = viz.popularidad_por_idiomas(datos_f).set_index("tramo")["mediana"]
    if {"1", "13 a 20"}.issubset(pop.index):
        bloque = ""
        if {"29", "Más de 29"}.issubset(pop.index):
            bloque = (
                f" Los tramos en ámbar caen a {pop['29']:.0f} (exactamente 29 idiomas) y "
                f"{pop['Más de 29']:.0f} (más de 29): reúnen juegos que marcan en bloque "
                "todos los idiomas, sin una localización real."
            )
        interpretacion(
            f"Los idiomas no se relacionan con la recepción (Spearman "
            f"{dec(_spearman('n_idiomas'))}), pero sí con la popularidad: la mediana de "
            f"reseñas pasa de {pop['1']:.0f} con un idioma a {pop['13 a 20']:.0f} con 13 a "
            f"20 idiomas.{bloque}"
        )

st.divider()

# Componente temporal
st.subheader("Componente temporal (T)")
grafico(viz.evolucion_recepcion(datos_f))
por_anio = con_y.groupby("anio")["pct_positivas"].median()
resenas_anio = datos_f.groupby("anio")["total_resenas"].median()
if len(por_anio) >= 2:
    a0, a1 = int(por_anio.index.min()), int(por_anio.index.max())
    interpretacion(
        f"La recepción mediana sube de {pct(por_anio[a0])} en {a0} a "
        f"{pct(por_anio[a1])} en {a1}. Se lee con cautela: en el mismo periodo la "
        f"mediana de reseñas baja de {resenas_anio[a0]:.0f} a {resenas_anio[a1]:.0f}. "
        "Los juegos recientes tienen menos reseñas, las primeras suelen venir de "
        "jugadores entusiastas, y los juegos antiguos que siguen visibles acumulan "
        "también las críticas de largo plazo."
    )

st.divider()

# Vision de conjunto
st.subheader("Visión de conjunto")
grafico(viz.matriz_correlacion(datos_f))
corrs = {
    "precio": _spearman("precio"),
    "número de sistemas operativos": _spearman("n_sistemas"),
    "total de reseñas": _spearman("total_resenas"),
    "número de idiomas": _spearman("n_idiomas"),
}
mayor = max(corrs, key=lambda k: abs(corrs[k]))
idiomas_pop = datos_f["n_idiomas"].corr(datos_f["total_resenas"], method="spearman")
interpretacion(
    f"Ninguna variable numérica tiene una correlación fuerte con la recepción. La "
    f"mayor en valor absoluto es {mayor} ({dec(corrs[mayor])}). En cambio, número de "
    f"idiomas y total de reseñas se mueven juntos ({dec(idiomas_pop)}), lo que refuerza "
    "que las características de publicación se asocian más a la popularidad que a la "
    "valoración."
)

st.divider()

# Prueba de robustez
st.subheader("Prueba de robustez")
st.markdown(
    f"Con pocas reseñas la proporción de positivas toma valores extremos: el "
    f"{pct((con_y['pct_positivas'] == 1).mean())} de los juegos con reseñas tiene "
    "exactamente 100 %. Para comprobar que los hallazgos no dependen de esos casos, "
    "la tabla compara los resultados actuales con los que se obtienen al exigir un "
    "mínimo de reseñas."
)
umbral = st.select_slider("Mínimo de reseñas para comparar", options=[5, 10, 25, 50, 100], value=10)


def _resumen(datos: pd.DataFrame) -> dict:
    y_ = datos.dropna(subset=["pct_positivas"])
    com = y_.groupby("comunidad")["pct_positivas"].median()
    tr = y_.groupby("tramo_precio", observed=True)["pct_positivas"].median()
    return {
        "Juegos con reseñas": num(len(y_)),
        "Mediana de reseñas positivas": pct(y_["pct_positivas"].median()),
        "Juegos bien recibidos": pct((y_["pct_positivas"] >= 0.8).mean()),
        "Spearman precio y recepción": dec(y_["precio"].corr(y_["pct_positivas"], method="spearman")),
        "Diferencia por comunidad (puntos)": dec((com.get(True, np.nan) - com.get(False, np.nan)) * 100, 1, signo=True),
        "Mejor tramo de precio": str(tr.idxmax()) if len(tr) else "s/d",
    }


tabla = pd.DataFrame({
    "Filtros actuales": _resumen(datos_f),
    f"Con {umbral} o más reseñas": _resumen(datos_f[datos_f["total_resenas"] >= umbral]),
})
st.dataframe(tabla, use_container_width=True)
interpretacion(
    "Si las dos columnas apuntan en la misma dirección, el hallazgo es robusto: no "
    "depende de los juegos con muy pocas reseñas. Las diferencias de magnitud son "
    "esperables, porque los juegos con más reseñas son, en promedio, más conocidos."
)

st.divider()

# Sintesis de hallazgos
st.subheader("Hallazgos preliminares")
st.markdown(
    """
1. **La recepción está concentrada en valores altos.** La mediana de reseñas
   positivas ronda el 81 % y cerca de la mitad de los juegos con reseñas supera el 80 %.
2. **Ninguna característica explica por sí sola la recepción.** Las correlaciones
   con precio, idiomas y sistemas operativos son débiles (menores a 0,15).
3. **El precio tiene una relación no lineal.** Los juegos de 2 a 15 USD son los
   mejor valorados; los gratuitos quedan algo por debajo y los más caros, muy por
   debajo (los de más de 100 USD mezclan software profesional y juegos de bajo esfuerzo).
4. **La comunidad no mejora la recepción.** Multijugador o Workshop se asocian a una
   valoración unos 2 puntos menor, contra lo que se esperaba.
5. **Los idiomas se asocian a la popularidad, no a la valoración.** Hasta unos 20
   idiomas, más idiomas acompañan a muchas más reseñas.
6. **La tendencia temporal está condicionada por el volumen de reseñas.** La
   recepción sube en los años recientes, pero esos juegos tienen muy pocas reseñas.
7. **Los resultados son robustos.** Exigir un mínimo de reseñas cambia las
   magnitudes, pero no la dirección de los hallazgos.

**Cómo refinan la pregunta.** Las características de publicación parecen explicar
mejor *cuánta atención* recibe un juego (popularidad) que *qué tan bien* es valorado.
Para el Avance 3 se propone separar ambos objetivos y controlar por el año de
lanzamiento y el volumen de reseñas. La página 4 reúne información complementaria
sobre tiempo de juego, idiomas específicos y señales de metadatos inflados.
"""
)
