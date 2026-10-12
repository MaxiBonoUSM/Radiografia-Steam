"""
Configuracion central del proyecto.

Reune en un solo lugar las constantes y los nombres de columna usados en todo
el analisis. El objetivo es que el notebook y la aplicacion Streamlit compartan
exactamente los mismos parametros, de modo que los resultados sean consistentes
entre ambos.
"""

from pathlib import Path

# Rutas base del repositorio
RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
RUTA_DATOS_RAW = RAIZ_PROYECTO / "data" / "raw" / "games.csv"
RUTA_DATOS_PROCESADOS = RAIZ_PROYECTO / "data" / "processed" / "games_clean.parquet"

# Ventana temporal del proyecto (ver justificacion en el Avance 1)
ANIO_INICIO = 2014
ANIO_FIN = 2024

# Minimo de resenas por defecto. Es 0 para no restringir la muestra: todos los
# juegos de la ventana entran en los analisis descriptivos, y los analisis de
# recepcion usan automaticamente los juegos con al menos una resena (sin resenas
# la proporcion de positivas no existe). El valor es ajustable en la aplicacion.
MIN_RESENAS_DEFECTO = 0

# Minimo de resenas usado como prueba de robustez. Con muy pocas resenas la
# proporcion de positivas toma valores extremos (un juego con una sola resena
# tiene 0 % o 100 %), por lo que los hallazgos se contrastan con este umbral.
MIN_RESENAS_ROBUSTEZ = 10

# Umbral de "bien recibido" inspirado en los tramos de valoracion de Steam.
# Un juego se considera bien recibido cuando al menos el 80 por ciento de sus
# resenas son positivas.
UMBRAL_BIEN_RECIBIDO = 0.80

# Numero de idiomas principales de Steam. Algunos juegos marcan en bloque todos
# los idiomas que permite la tienda (hasta 103), lo que no refleja una
# localizacion real. Esos juegos no se eliminan: se identifican con una columna
# indicadora y se muestran como un grupo aparte en el analisis de idiomas.
MAX_IDIOMAS_PLAUSIBLE = 29

# Paleta visual del proyecto (coherente con la presentacion del Avance 1)
COLORES = {
    "navy": "#1B2838",
    "panel": "#2A475E",
    "steam": "#66C0F4",
    "deep": "#1C6EA4",
    "ice": "#AEC7DA",
    "ambar": "#E8A33D",
    "verde": "#5BA86F",
    "rojo": "#C0504D",
    "gris": "#5B6B7A",
}

# Secuencia de colores para series categoricas
SECUENCIA_COLORES = [
    "#1C6EA4", "#66C0F4", "#E8A33D", "#5BA86F",
    "#C0504D", "#8E7CC3", "#2A475E", "#AEC7DA",
]

# Resolvedor de nombres de columna.
# Cada clave canonica apunta a una lista de posibles nombres en el archivo de
# origen. Esto permite trabajar tanto con el CSV de Kaggle (Title Case) como con
# la version snake_case del dataset sin modificar el resto del codigo.
ALIAS_COLUMNAS = {
    "app_id": ["AppID", "appid", "app_id", "appID"],
    "nombre": ["Name", "name"],
    "fecha_lanzamiento": ["Release date", "release_date"],
    "precio": ["Price", "price"],
    "positivas": ["Positive", "positive"],
    "negativas": ["Negative", "negative"],
    "generos": ["Genres", "genres"],
    "categorias": ["Categories", "categories"],
    "idiomas": ["Supported languages", "supported_languages"],
    "windows": ["Windows", "windows"],
    "mac": ["Mac", "mac"],
    "linux": ["Linux", "linux"],
    "playtime_medio": ["Average playtime forever", "average_playtime_forever"],
    "playtime_mediano": ["Median playtime forever", "median_playtime_forever"],
    "duenos_estimados": ["Estimated owners", "estimated_owners"],
    "peak_ccu": ["Peak CCU", "peak_ccu"],
    "dlc_count": ["DLC count", "dlc_count"],
    "recomendaciones": ["Recommendations", "recommendations"],
    "metacritic": ["Metacritic score", "metacritic_score"],
}

# Etiquetas legibles para mostrar en los graficos
ETIQUETAS = {
    "pct_positivas": "Proporción de reseñas positivas",
    "precio": "Precio (USD)",
    "total_resenas": "Total de reseñas",
    "n_idiomas": "Número de idiomas soportados",
    "playtime_mediano": "Tiempo de juego mediano (min)",
    "anio": "Año de lanzamiento",
    "n_sistemas": "Número de sistemas operativos",
    "n_generos": "Número de géneros declarados",
    "genero_principal": "Género principal",
}
