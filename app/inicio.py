"""
Pagina de inicio.

Recuerda brevemente el contexto del proyecto definido en el Avance 1 (problema,
pregunta, alcance y la estructura X, Y, T) y explica como navegar las tres
paginas analiticas.
"""

import streamlit as st

from _shared import encabezado, obtener_datos, num, COLORES

encabezado(
    "Radiografía de Steam",
    "Características de publicación y recepción de videojuegos (2014 a 2024)",
)

st.markdown(
    "Esta aplicación presenta el Análisis Exploratorio de Datos del proyecto. Su "
    "objetivo es pasar de la pregunta **qué queremos estudiar** a la pregunta "
    "**qué nos dicen realmente los datos**."
)

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("El problema")
    st.write(
        "Steam es la principal plataforma de videojuegos para PC. El volumen de "
        "lanzamientos creció hasta saturar el mercado: la mayoría de los títulos "
        "recibe poca visibilidad y muy pocas reseñas. En ese contexto no es "
        "evidente qué características de un juego se asocian a una mejor recepción."
    )

    st.subheader("Pregunta principal")
    st.markdown(
        f"<div style='background:{COLORES['ice']};padding:14px 18px;border-radius:8px;"
        f"color:{COLORES['navy']}'>"
        "¿Cómo se relacionan las características de un juego en Steam (género, "
        "precio, idiomas, soporte multiplataforma y funcionalidades comunitarias) "
        "con su recepción y el compromiso de los jugadores, en los títulos "
        "publicados entre 2014 y 2024?"
        "</div>",
        unsafe_allow_html=True,
    )

with col2:
    st.subheader("Estructura del análisis")
    st.markdown(
        """
- **X (información disponible):** género, precio, idiomas, sistema operativo,
  funcionalidades comunitarias, DLC y fecha.
- **Y (fenómeno objetivo):** proporción de reseñas positivas, tiempo de juego
  mediano y volumen de reseñas.
- **T (contexto temporal):** títulos publicados entre 2014 y 2024.
"""
    )

st.divider()

st.subheader("Cómo navegar")
st.markdown(
    """
Use el menú lateral para recorrer las páginas analíticas:

1. **Contexto y Datos:** qué estudiamos y con qué datos. Estructura y calidad del dataset.
2. **Análisis Exploratorio:** cómo se comportan nuestros datos. Distribuciones y comparaciones.
3. **Análisis de la Pregunta:** qué hemos aprendido. Relaciones entre X e Y, componente temporal, robustez y hallazgos.
4. **Información complementaria:** tiempo de juego, idiomas específicos y señales de metadatos inflados, como contexto para grupos específicos.

Los filtros del panel lateral (año, mínimo de reseñas, precio y género) modifican
todas las visualizaciones y sus interpretaciones, de modo que el análisis es interactivo.
"""
)

# Verificacion temprana de la fuente de datos
datos = obtener_datos()
if datos is not None:
    st.success(f"Datos cargados correctamente: {num(len(datos))} juegos en la ventana 2014 a 2024.")
    st.caption("Si cambia la fuente o los filtros, las páginas se actualizan de forma automática.")
