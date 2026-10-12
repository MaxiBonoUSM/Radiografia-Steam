"""
Aplicacion Streamlit: Radiografia de Steam (Avance 2).

Punto de entrada y enrutador de la aplicacion. Define la configuracion general
de la pagina y el menu de navegacion. Se usa st.navigation para nombrar cada
pagina con su titulo completo (con tildes), en lugar de depender del nombre del
archivo.

Ejecutar desde la raiz del repositorio con:
    streamlit run app/app.py
"""

import streamlit as st

st.set_page_config(
    page_title="Radiografía de Steam",
    page_icon="🎮",
    layout="wide",
)

navegacion = st.navigation([
    st.Page("inicio.py", title="Inicio", default=True),
    st.Page("pages/1_Contexto_y_Datos.py", title="1. Contexto y Datos"),
    st.Page("pages/2_Analisis_Exploratorio.py", title="2. Análisis Exploratorio"),
    st.Page("pages/3_Analisis_de_la_Pregunta.py", title="3. Análisis de la Pregunta"),
    st.Page("pages/4_Informacion_Complementaria.py", title="4. Información complementaria"),
])
navegacion.run()
