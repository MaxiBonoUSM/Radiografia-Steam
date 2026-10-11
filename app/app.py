"""
Aplicacion Streamlit: Radiografia de Steam (Avance 2).

Punto de entrada de la aplicacion. Esta pagina de inicio recuerda brevemente el
contexto del proyecto definido en el Avance 1 (problema, pregunta, alcance y la
estructura X, Y, T) y explica como navegar las tres paginas analiticas.

Ejecutar con:
    streamlit run app/app.py
"""

import streamlit as st

from _shared import encabezado, obtener_datos, COLORES

st.set_page_config(
    page_title="Radiografia de Steam",
    page_icon="chart",
    layout="wide",
)

encabezado(
    "Radiografia de Steam",
    "Caracteristicas de publicacion y recepcion de videojuegos (2014 a 2024)",
)

st.markdown(
    """
Esta aplicacion presenta el Analisis Exploratorio de Datos del proyecto.
Su objetivo es pasar de la pregunta **que queremos estudiar** a la pregunta
**que nos dicen realmente los datos**.
"""
)

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("El problema")
    st.write(
        "Steam es la principal plataforma de videojuegos para PC. El volumen de "
        "lanzamientos crecio hasta saturar el mercado: la mayoria de los titulos "
        "recibe poca visibilidad y muy pocas resenas. En ese contexto no es "
        "evidente que caracteristicas de un juego se asocian a una mejor recepcion."
    )

    st.subheader("Pregunta principal")
    st.markdown(
        f"<div style='background:{COLORES['ice']};padding:14px 18px;border-radius:8px;"
        f"color:{COLORES['navy']}'>"
        "Como se relacionan las caracteristicas de un juego en Steam (genero, "
        "precio, idiomas, soporte multiplataforma y funcionalidades comunitarias) "
        "con su recepcion y el compromiso de los jugadores, en los titulos "
        "publicados entre 2014 y 2024?"
        "</div>",
        unsafe_allow_html=True,
    )

with col2:
    st.subheader("Estructura del analisis")
    st.markdown(
        """
- **X (informacion disponible):** genero, precio, idiomas, sistema operativo,
  funcionalidades comunitarias, DLC y fecha.
- **Y (fenomeno objetivo):** proporcion de resenas positivas, tiempo de juego
  mediano y volumen de resenas.
- **T (contexto temporal):** titulos publicados entre 2014 y 2024.
"""
    )

st.divider()

st.subheader("Como navegar")
st.markdown(
    """
Use el menu lateral para recorrer las tres paginas analiticas:

1. **Contexto y Datos:** que estudiamos y con que datos. Estructura y calidad del dataset.
2. **Analisis Exploratorio:** como se comportan nuestros datos. Distribuciones y comparaciones.
3. **Analisis de la Pregunta:** que hemos aprendido. Relaciones entre X e Y y componente temporal.

Los filtros del panel lateral (anio, minimo de resenas, precio y genero) modifican
todas las visualizaciones, de modo que el analisis es interactivo.
"""
)

# Verificacion temprana de la fuente de datos
datos = obtener_datos()
if datos is not None:
    st.success(
        f"Datos cargados correctamente: {len(datos):,} juegos en la ventana "
        f"2014 a 2024.".replace(",", ".")
    )
    st.caption(
        "Si cambia la fuente o los filtros, las paginas se actualizan de forma automatica."
    )
