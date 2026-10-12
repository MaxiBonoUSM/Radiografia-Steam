"""
Pagina 4: Informacion complementaria.

Proposito analitico: reunir informacion que no responde directamente la pregunta
principal, pero que aporta contexto pertinente para grupos especificos. Incluye
tres bloques:

  1. Tiempo de juego, analizado solo en el subgrupo de juegos que lo tiene
     registrado (la fuente no lo mide para la mayoria).
  2. Idiomas en detalle: que idiomas se soportan y como se comparan los juegos
     que soportan un idioma concreto con los que no lo hacen.
  3. Senales de metadatos inflados: juegos que declaran demasiados generos o
     todos los idiomas, y registros de software dentro del catalogo.

Las interpretaciones se calculan a partir de los datos filtrados.
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from _shared import (  # noqa: E402
    encabezado, obtener_datos, aplicar_filtros, grafico, interpretacion, pct, num, dec,
)
from src import viz  # noqa: E402

encabezado("4. Información complementaria",
           "Datos parciales que aportan contexto para grupos específicos")

datos = obtener_datos()
if datos is None:
    st.stop()

datos_f = aplicar_filtros(datos)
if len(datos_f) < 30:
    st.warning("Los filtros actuales dejan muy pocos juegos. Amplíe los rangos del panel lateral.")
    st.stop()

st.markdown(
    "Esta página reúne información que no responde por sí sola la pregunta del "
    "proyecto, ya sea porque cubre solo una parte de los juegos o porque describe "
    "casos particulares. Se presenta como contexto y como base para preguntas más "
    "específicas, no como conclusión general."
)

# ---------------------------------------------------------------------------
# 1. Tiempo de juego
# ---------------------------------------------------------------------------
st.subheader("Tiempo de juego (solo juegos con registro)")

tiempo = viz.con_tiempo_registrado(datos_f)
sin_registro = datos_f[datos_f["playtime_mediano"] == 0]
c1, c2, c3 = st.columns(3)
c1.metric("Juegos con tiempo registrado", pct(len(tiempo) / len(datos_f)),
          help=f"{num(len(tiempo))} de {num(len(datos_f))} juegos filtrados")
c2.metric("Horas medianas de juego", f"{dec(tiempo['horas'].median(), 1)} h" if len(tiempo) else "s/d")
c3.metric("Mediana de reseñas: con registro / sin registro",
          f"{tiempo['total_resenas'].median():.0f} / {sin_registro['total_resenas'].median():.0f}"
          if len(tiempo) and len(sin_registro) else "s/d")

if len(tiempo) >= 30:
    col_a, col_b = st.columns(2)
    with col_a:
        grafico(viz.tiempo_por_tramo_precio(datos_f))
    with col_b:
        grafico(viz.tiempo_por_genero(datos_f))

    sp_precio = tiempo["horas"].corr(tiempo["precio"], method="spearman")
    sp_recep = tiempo["horas"].corr(tiempo["pct_positivas"], method="spearman")
    interpretacion(
        f"El tiempo de juego solo está registrado en el {pct(len(tiempo) / len(datos_f))} "
        "de los juegos, y esos juegos tienen muchas más reseñas que el resto: el "
        "registro se concentra en títulos con más audiencia, por lo que estas cifras no "
        "representan a todo el catálogo. Dentro de ese grupo, el precio se asocia con "
        f"más horas de juego (Spearman {dec(sp_precio)}): los juegos más caros suelen "
        "ofrecer más contenido. En cambio, el tiempo de juego casi no se relaciona con "
        f"la recepción (Spearman {dec(sp_recep)}). Los tramos con muy pocos juegos "
        "(visibles al pasar el cursor) no deben interpretarse."
    )
else:
    st.info("Con los filtros actuales hay muy pocos juegos con tiempo de juego registrado.")

st.divider()

# ---------------------------------------------------------------------------
# 2. Idiomas en detalle
# ---------------------------------------------------------------------------
st.subheader("Idiomas en detalle")

todos = viz.explotar_idiomas(datos_f)["idioma"].value_counts()
opciones = todos.index.tolist()
defecto = "Spanish - Latin America"
idioma = st.selectbox(
    "Idioma a analizar", opciones,
    index=opciones.index(defecto) if defecto in opciones else 0,
    help="Compara los juegos que soportan el idioma con los que no lo soportan.",
)

grafico(viz.idiomas_mas_frecuentes(datos_f, destacar=idioma))

comp = viz.comparar_idioma(datos_f, idioma)
c1, c2, c3 = st.columns(3)
c1.metric(f"Juegos con {idioma}", num(comp["juegos_con"]))
c2.metric("Mediana de reseñas (con / sin)",
          f"{comp['resenas_con']:.0f} / {comp['resenas_sin']:.0f}")
c3.metric("Recepción mediana (con / sin)",
          f"{pct(comp['recepcion_con'])} / {pct(comp['recepcion_sin'])}")

if comp["juegos_con"] > 0:
    dif = (comp["recepcion_con"] - comp["recepcion_sin"]) * 100
    interpretacion(
        f"El inglés está presente en casi todos los juegos, y el segundo idioma más "
        f"soportado es {todos.index[1] if len(todos) > 1 else 's/d'}. Los juegos que "
        f"soportan {idioma} tienen una mediana de {comp['resenas_con']:.0f} reseñas, "
        f"frente a {comp['resenas_sin']:.0f} de los que no lo soportan, y una recepción "
        f"{'mayor' if dif > 0 else 'menor'} ({dec(dif, 1, signo=True)} puntos). La "
        "comparación es descriptiva: localizar a un idioma suele ser propio de juegos "
        "con más presupuesto, así que la diferencia no se debe solo al idioma."
    )

st.divider()

# ---------------------------------------------------------------------------
# 3. Senales de metadatos inflados
# ---------------------------------------------------------------------------
st.subheader("Señales de metadatos inflados")

grafico(viz.recepcion_por_n_generos(datos_f))
con_y = datos_f.dropna(subset=["n_generos", "pct_positivas"])
pocos = con_y[con_y["n_generos"] <= 2]["pct_positivas"].median()
muchos = con_y[con_y["n_generos"] > 8]["pct_positivas"].median()
n_muchos = int((con_y["n_generos"] > 8).sum())
if n_muchos > 0:
    interpretacion(
        f"Los juegos que declaran 1 o 2 géneros tienen una recepción mediana de "
        f"{pct(pocos)}, mientras que los {num(n_muchos)} que declaran más de 8 bajan a "
        f"{pct(muchos)}. Marcar casi todos los géneros parece una forma de ganar "
        "visibilidad en las búsquedas más que una descripción del juego, y se asocia a "
        "una peor valoración."
    )

atip = datos_f[datos_f["idiomas_atipico"].fillna(False)]
caros = datos_f[datos_f["precio"] > 100]
col_a, col_b = st.columns(2)
with col_a:
    st.markdown("**Idiomas marcados en bloque**")
    if len(atip):
        st.markdown(
            f"{num(len(atip))} juegos declaran más de 29 idiomas. El "
            f"{pct((atip['total_resenas'] == 0).mean())} no tiene ninguna reseña y su "
            f"precio mediano es {dec(atip['precio'].median())} USD: el patrón calza con "
            "juegos de bajo esfuerzo que marcan todas las opciones de la tienda."
        )
    else:
        st.caption("No hay juegos con idiomas marcados en bloque en la selección actual.")
with col_b:
    st.markdown("**Juegos de más de 100 USD**")
    if len(caros):
        caros_y = caros.dropna(subset=["pct_positivas"])
        st.markdown(
            f"{num(len(caros))} registros superan los 100 USD; {num(len(caros_y))} tienen "
            f"reseñas, con una recepción mediana de {pct(caros_y['pct_positivas'].median())}. "
            "El grupo mezcla software profesional (por ejemplo, Houdini Indie o Substance "
            "3D Modeler, bien valorados) con juegos de bajo esfuerzo a 199,99 USD que "
            "marcan casi todos los géneros y reciben malas reseñas."
        )
    else:
        st.caption("No hay juegos de más de 100 USD en la selección actual.")
