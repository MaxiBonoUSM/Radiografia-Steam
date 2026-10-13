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

from _shared import (  # noqa: E402
    encabezado, obtener_datos, obtener_calidad, aplicar_filtros, grafico,
    interpretacion, pct, num,
)
from src import config, viz  # noqa: E402

encabezado("1. Contexto y Datos", "¿Qué estamos estudiando y con qué datos?")

datos = obtener_datos()
if datos is None:
    st.stop()

datos_f = aplicar_filtros(datos)
if datos_f.empty:
    st.warning("Los filtros actuales no dejan juegos. Amplíe los rangos del panel lateral.")
    st.stop()

# Indicadores generales
st.subheader("Indicadores generales")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Juegos (filtrados)", num(len(datos_f)))
c2.metric("Con al menos una reseña", num(datos_f["pct_positivas"].notna().sum()),
          help="Solo estos juegos tienen proporción de reseñas positivas.")
c3.metric("Periodo", f"{int(datos_f['anio'].min())}-{int(datos_f['anio'].max())}")
c4.metric("Mediana de reseñas positivas", pct(datos_f["pct_positivas"].median()))
c5.metric("Juegos bien recibidos", pct(datos_f["bien_recibido"].mean()),
          help=f"Al menos {config.UMBRAL_BIEN_RECIBIDO:.0%} de reseñas positivas, "
               "sobre los juegos con reseñas")

st.divider()

# Estructura y calidad de los datos
st.subheader("Estructura y calidad de los datos")

calidad, filas_crudo = obtener_calidad()
chq = st.session_state.get("chequeos") or {}
chq_texto = (
    f"no hay AppID repetidos ({chq.get('appid_duplicados', 's/d')}) ni filas idénticas "
    f"({chq.get('filas_identicas', 's/d')}). {num(chq.get('juegos_nombre_compartido', 0))} "
    f"juegos comparten nombre con otro ({num(chq.get('nombres_compartidos', 0))} nombres), "
    "pero tienen AppID distinto: son homónimos, no duplicados, y se conservan. No hay "
    f"precios ni reseñas negativos ({chq.get('valores_negativos', 's/d')}). Las fechas van "
    f"de {chq.get('anio_min', 's/d')} a {chq.get('anio_max', 's/d')}; los juegos fuera de "
    "2014 a 2024 quedan fuera del alcance. No hay cobertura espacial: la fuente no "
    "informa la ubicación de los jugadores."
)
sin_resenas = int((datos["total_resenas"] == 0).sum())
idiomas_atip = int(datos["idiomas_atipico"].sum())
playtime_registrado = (datos["playtime_mediano"] > 0).mean()
GENEROS_SOFTWARE = {
    "Utilities", "Design & Illustration", "Animation & Modeling", "Video Production",
    "Audio Production", "Software Training", "Web Publishing", "Photo Editing",
    "Education", "Accounting", "Game Development",
}
solo_software = int(datos["generos"].fillna("").str.split(",").map(
    lambda lista: {g.strip() for g in lista if g.strip()}
).map(lambda gs: bool(gs) and gs <= GENEROS_SOFTWARE).sum())
st.markdown(
    f"""
El archivo original tiene **{num(filas_crudo or 0)} juegos** (un juego por fila). Tras
acotar a 2014 a 2024 quedan **{num(len(datos))}**, de los cuales **{num(sin_resenas)}**
({pct(sin_resenas / len(datos))}) no tiene ninguna reseña. Problemas encontrados y
decisiones tomadas:

- **Encabezado desalineado:** el CSV original fusiona las columnas "Discount" y
  "DLC count" en un solo nombre, lo que desplaza todos los valores una posición. Sin
  corregirlo, la columna de fecha contiene los tramos de propietarios y ninguna
  fecha es interpretable. La carga separa ese nombre para realinear las columnas.
- **Duplicados y valores imposibles:** {chq_texto}
- **Cobertura temporal:** se interpreta la fecha de lanzamiento (formato "Aug 1,
  2023") y se acota la ventana a 2014 a 2024.
- **Indicador de recepción:** proporción de reseñas positivas sobre el total. Es
  indefinida cuando el juego no tiene reseñas.
- **Sin restricciones de muestra:** no se excluye ningún juego por precio ni por
  número de reseñas. Los análisis de recepción usan automáticamente los juegos con
  al menos una reseña, porque sin reseñas la proporción de positivas no existe. El
  mínimo de reseñas es ajustable en el panel lateral como prueba de robustez.
- **Campos de múltiples valores:** géneros, categorías e idiomas se procesan para
  obtener las funcionalidades comunitarias, el número de géneros y el conteo de
  idiomas. Como los géneros vienen casi siempre en orden alfabético, el análisis por
  género es multietiqueta.
- **Idiomas marcados en bloque:** {num(idiomas_atip)} juegos declaran más de 29
  idiomas (hasta 103, es decir, todos los que permite la tienda). No se eliminan:
  se muestran como un grupo aparte porque no reflejan una localización real.
- **Tiempo de juego parcial:** solo el {pct(playtime_registrado)} de los juegos tiene
  tiempo de juego registrado (el resto vale 0 porque la fuente no lo mide). Se usa
  como información complementaria sobre ese subgrupo (página 4).
- **Software dentro del catálogo:** {num(solo_software)} registros declaran solo
  géneros de software (por ejemplo, Utilities o Animation & Modeling), aunque la
  fuente dice incluir únicamente juegos. Se conservan y se pueden aislar con el
  filtro de géneros.
- **Columnas descartadas:** las de texto extenso (descripciones, capturas, enlaces)
  no aportan a la pregunta y se omiten al leer.
"""
)

if calidad is not None:
    st.markdown("**Valores faltantes por columna (archivo original, columnas utilizadas)**")
    st.dataframe(calidad, use_container_width=True, height=320)
    peores = calidad[calidad["pct_nulos"] > 0].head(3)
    if not peores.empty:
        detalle = ", ".join(f"{r.columna} ({r.pct_nulos:.0f} %)" for r in peores.itertuples())
        interpretacion(
            f"Las columnas con más faltantes son {detalle}. Ninguna es necesaria para "
            "la pregunta: precio, reseñas, fecha, géneros e idiomas están casi completos."
        )

st.divider()

# Contexto temporal
st.subheader("Contexto temporal del catálogo")
anios_sel = datos_f["anio"].agg(["min", "max"])
catalogo = datos[datos["anio"].between(anios_sel["min"], anios_sel["max"])]
grafico(viz.releases_por_anio(catalogo))
conteo = catalogo.groupby("anio").size()
if len(conteo) >= 2:
    a0, a1 = int(conteo.index.min()), int(conteo.index.max())
    interpretacion(
        f"Los lanzamientos pasan de {num(conteo[a0])} en {a0} a {num(conteo[a1])} en "
        f"{a1} (unas {conteo[a1] / conteo[a0]:.0f} veces más). Este gráfico considera "
        "todos los juegos del periodo, con o sin reseñas, porque busca dimensionar la "
        "saturación del mercado que motiva el proyecto."
    )
