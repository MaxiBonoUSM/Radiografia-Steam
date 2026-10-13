Radiografía de Steam: características de publicación y recepción de videojuegos (2014 a 2024)

Proyecto de la asignatura EIN092B Visualización (2026-II). Estado actual: Avance 2, Análisis Exploratorio de
Datos (EDA) y aplicación interactiva en Streamlit.

Integrantes

- Maximiliano Bono

Descripción breve del problema

Steam es la principal plataforma de distribución de videojuegos para PC. El volumen de títulos publicados
cada año ha crecido de forma sostenida, pasando de unos pocos cientos anuales antes de 2014 a más de diez
mil por año en el periodo reciente. Este crecimiento generó un mercado altamente saturado, en el que la
mayoría de los juegos recibe poca visibilidad y muy pocas reseñas.

En ese contexto, resulta difícil identificar qué características de un juego (su precio, su género, la cantidad
de idiomas soportados, el soporte multiplataforma, las funcionalidades comunitarias o el momento de
lanzamiento) se asocian a una mejor recepción por parte de los jugadores. El problema consiste en describir y
visualizar esas relaciones a partir de datos públicos.

Motivación

Comprender estas relaciones tiene valor práctico para estudios independientes, analistas del sector y personas
interesadas en la industria. Permite apoyar decisiones sobre alcance, precio, localización de idiomas y
selección de funcionalidades antes de publicar un título. Además, es un fenómeno con abundante información
pública, con variables numéricas, categóricas y temporales, lo que lo hace especialmente adecuado para
construir visualizaciones significativas.

Pregunta inicial

¿Cómo se relacionan las características de publicación y diseño de un videojuego en Steam (género, precio,
número de idiomas soportados, soporte multiplataforma y funcionalidades comunitarias) con su nivel de
recepción y compromiso de los jugadores, en los títulos publicados entre 2014 y 2024?

Estructura de la pregunta:

- X (información disponible): género, precio, número de idiomas soportados, soporte de sistemas operativos
  (Windows, Mac, Linux), funcionalidades comunitarias (multijugador, Steam Workshop), presencia de DLC y mes o
  año de lanzamiento.
- Y (objetivo o fenómeno de interés): recepción, medida como proporción de reseñas positivas, y compromiso,
  medido a través del tiempo de juego mediano y del volumen de reseñas como aproximación a la popularidad.
- T (contexto temporal): juegos publicados entre 2014 y 2024. El componente temporal delimita el periodo de
  análisis y permite comparar patrones entre años de lanzamiento.

Alcance

- Unidad de observación: un videojuego publicado en Steam (identificado por su AppID).
- Población: títulos publicados entre 2014 y 2024. No se restringe la muestra por precio ni por número de
  reseñas: los análisis descriptivos usan todos los juegos de la ventana, y los análisis de recepción usan los
  juegos con al menos una reseña, porque sin reseñas la proporción de positivas no existe. La robustez de los
  indicadores de recepción se comprueba exigiendo un mínimo de reseñas (prueba de robustez en la aplicación).
- Fenómeno estudiado: relación entre características del juego y su recepción o compromiso.
- Fuera de alcance: ventas monetarias reales, análisis de texto de las reseñas, comportamiento individual
  de jugadores y análisis geográfico detallado (la fuente no entrega ubicación de los usuarios).

Un alcance adecuado para este proyecto es concreto, medible, visualizable y abordable con los datos disponibles.

Fuente del dataset

Steam Games Dataset, mantenido por Fronkon Games. Los datos se generan con un scraper de código abierto
(licencia MIT) que consume la API oficial de Steam y complementa con información de SteamSpy.

- Hugging Face: https://huggingface.co/datasets/FronkonGames/steam-games-dataset
- Kaggle: https://www.kaggle.com/datasets/fronkongames/steam-games-dataset
- Código del scraper: https://github.com/FronkonGames/Steam-Games-Scraper

La versión utilizada en este avance (games.csv de Kaggle) contiene 125.855 juegos, de los cuales 95.595 fueron
publicados entre 2014 y 2024. La cifra exacta varía según la fecha de extracción del dataset.

Cómo obtener los datos

El archivo pesa cerca de 400 MB, por lo que no se versiona en el repositorio ni se incluye en `data/raw/`.
Para reproducir el proyecto:

1. Descargar `games.csv` desde Kaggle o Hugging Face usando cualquiera de los enlaces anteriores.
2. Colocar el archivo en `data/raw/games.csv`.
3. Ejecutar la aplicación o los notebooks según las instrucciones de la sección siguiente.

El encabezado del CSV original une las columnas "Discount" y "DLC count" en un solo nombre, lo que desplaza
todos los valores una posición. El código corrige este error de forma automática al leer el archivo. También
tolera la versión del dataset con nombres de columna en minúscula (snake_case).

Cómo ejecutar la aplicación

```bash
# 1. Crear y activar un entorno virtual (opcional pero recomendado)
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate

# 2. Instalar las dependencias
pip install -r requirements.txt

# 3. Colocar games.csv en data/raw/ (ver sección anterior)

# 4. Ejecutar la aplicación desde la raíz del repositorio
streamlit run app/app.py
```

La aplicación se abre en el navegador (por defecto en http://localhost:8501). El comando debe ejecutarse desde
la raíz del repositorio, para que Streamlit encuentre el tema visual definido en `.streamlit/config.toml`. Si el
archivo no está en `data/raw/`, la aplicación permite subir el CSV desde el panel lateral.

Para revisar el análisis en formato de informe:

```bash
jupyter notebook notebooks/02_eda.ipynb
```

Dependencias principales

pandas, numpy, plotly, streamlit (versión 1.40 o superior), statsmodels, matplotlib, seaborn y pyarrow. El
detalle de versiones mínimas está en `requirements.txt`.

Breve descripción de los datos

Cada fila representa un juego publicado en Steam. Entre las variables principales se encuentran:

- Identificación: AppID, nombre.
- Temporal: fecha de lanzamiento.
- Numéricas: precio (USD), cantidad de DLC, reseñas positivas, reseñas negativas, recomendaciones, pico de
  usuarios concurrentes, puntaje Metacritic, tiempos de juego (promedio y mediano).
- Categóricas y de texto: géneros, categorías (por ejemplo, multijugador o Steam Workshop), etiquetas,
  idiomas soportados, desarrolladores, publicadores.
- Booleanas: soporte para Windows, Mac y Linux.
- Rangos: estimación de propietarios (por tramos, provista por SteamSpy).

A partir de estas variables se derivan indicadores como la proporción de reseñas positivas
(positivas / (positivas + negativas)), el número de idiomas soportados, el número de géneros declarados, el
número de sistemas operativos y la presencia de funcionalidades comunitarias.

Descripción de las páginas de la aplicación

La aplicación tiene una página de inicio y cuatro páginas analíticas, cada una con un propósito reconocible:

- Inicio: recuerda el problema, la pregunta, el alcance y la estructura X, Y y T, y confirma la carga de datos.
- 1. Contexto y Datos: responde "qué estamos estudiando y con qué datos". Indicadores generales, revisión de
  calidad (faltantes, duplicados, valores fuera de rango, categorías inconsistentes, cobertura temporal),
  decisiones de limpieza y lanzamientos por año.
- 2. Análisis Exploratorio: responde "cómo se comportan nuestros datos". Distribución de la recepción y del
  precio, frecuencia de géneros, recepción por género y estadísticas descriptivas.
- 3. Análisis de la Pregunta: responde "qué hemos aprendido hasta ahora". Relaciones entre X e Y (precio,
  comunidad, idiomas), evolución temporal, matriz de correlación, prueba de robustez y síntesis de hallazgos.
- 4. Información complementaria: reúne datos parciales o de grupos específicos que aportan contexto: tiempo de
  juego (solo juegos con registro), idiomas en detalle (con un selector de idioma) y señales de metadatos
  inflados (demasiados géneros o idiomas, juegos de más de 100 USD).

Los filtros del panel lateral (año de lanzamiento, mínimo de reseñas, rango de precio y géneros) modifican
todas las visualizaciones y sus interpretaciones. Los textos bajo cada gráfico se recalculan con los datos
filtrados, de modo que siempre describen lo que se ve en pantalla. La aplicación contiene 15 visualizaciones
interactivas (Plotly) en 7 tipos distintos: histograma, barras, boxplot, violín, dispersión, línea y mapa de
calor.

Decisiones de limpieza

- Se corrige el encabezado del CSV original, que une las columnas "Discount" y "DLC count".
- Se omiten al leer las columnas de texto extenso (descripciones, capturas, enlaces), que no aportan a la
  pregunta y elevan el uso de memoria.
- Se interpreta la fecha de lanzamiento (formato "Aug 1, 2023") y se acota la ventana a 2014 a 2024.
- La proporción de reseñas positivas se calcula como positivas sobre el total y queda vacía cuando el juego no
  tiene reseñas (20.425 juegos, 21 % de la ventana).
- No se aplican topes de precio ni mínimos de reseñas por defecto; el mínimo es ajustable y se usa como prueba
  de robustez.
- 1.804 juegos declaran más de 29 idiomas (hasta 103, todos los que permite la tienda). Son metadatos marcados
  en bloque: se conservan y se muestran como un grupo aparte.
- Solo el 23 % de los juegos tiene tiempo de juego registrado (el resto vale 0 porque la fuente no lo mide). Se
  analiza como información complementaria sobre ese subgrupo.
- Los géneros vienen casi siempre en orden alfabético, por lo que el análisis por género es multietiqueta: cada
  juego cuenta en todos los géneros que declara.
- No hay AppID duplicados ni filas idénticas. Los juegos que comparten nombre tienen AppID distinto, por lo que
  son homónimos y se conservan.
- 1.075 registros declaran solo géneros de software, aunque la fuente dice incluir únicamente juegos. Se
  conservan, se declaran como limitación y pueden aislarse con el filtro de géneros.

Hallazgos preliminares

- La recepción se concentra en valores altos: la mediana es 81 % de reseñas positivas y el 53 % de los juegos
  con reseñas supera el 80 %.
- Ninguna característica explica por sí sola la recepción: las correlaciones de Spearman con precio, idiomas y
  sistemas operativos son menores a 0,15.
- El precio tiene una relación no lineal (U invertida): los juegos de 2 a 15 USD son los mejor valorados y los
  de más de 40 USD caen con claridad.
- Los juegos con multijugador o Steam Workshop se valoran algo peor que el resto (80 % frente a 82 %).
- Los idiomas se asocian a la popularidad (número de reseñas), no a la valoración.
- La recepción mediana sube de 74 % (2014) a 89 % (2024), pero la mediana de reseñas cae de 314 a 3, por lo
  que la tendencia se lee con cautela.
- Los resultados se mantienen al exigir un mínimo de 10 reseñas.

A partir de estos resultados, la pregunta se refina: las características de publicación parecen explicar mejor
cuánta atención recibe un juego (popularidad) que qué tan bien es valorado. Para el Avance 3 se propone separar
ambos objetivos y controlar por año de lanzamiento y volumen de reseñas.

Limitaciones conocidas

Los datos son un corte transversal: las métricas acumuladas favorecen a los juegos más antiguos. Solo hay
juegos publicados, lo que introduce sesgo de supervivencia. El tiempo de juego está registrado solo para una
parte del catálogo, en su mayoría juegos populares. No se dispone de ventas reales ni de información geográfica
de los usuarios, y las comparaciones son descriptivas, por lo que no permiten afirmar causalidad.

Documentación

- `docs/Informe_Avance2_Radiografia_Steam.pdf`: informe técnico con el funcionamiento del código, el
  cumplimiento de la guía del Avance 2, los descubrimientos y las definiciones de los conceptos utilizados.
- `docs/Avance2_Radiografia_Steam.pptx`: presentación de apoyo para la defensa.

Estructura general del repositorio

```
proyecto-visualizacion/
|
|-- .streamlit/
|   '-- config.toml                tema visual de la aplicación
|
|-- app/
|   |-- app.py                     punto de entrada y menú de navegación
|   |-- inicio.py                  página de inicio
|   |-- _shared.py                 carga con caché, filtros y formato compartidos
|   '-- pages/
|       |-- 1_Contexto_y_Datos.py
|       |-- 2_Analisis_Exploratorio.py
|       |-- 3_Analisis_de_la_Pregunta.py
|       '-- 4_Informacion_Complementaria.py
|
|-- data/
|   |-- raw/                       datos originales sin modificar (no versionados)
|   '-- processed/                 datos generados tras limpieza y transformación
|
|-- docs/                          informe técnico y presentaciones
|-- figures/                       gráficos y recursos visuales
|
|-- notebooks/
|   |-- 01_exploracion.ipynb       carga y estructura de los datos (Avance 1)
|   '-- 02_eda.ipynb               análisis exploratorio de datos (Avance 2)
|
|-- src/
|   |-- config.py                  constantes, rutas y alias de columnas
|   |-- data_loading.py            carga, limpieza y revisión de calidad
|   '-- viz.py                     funciones de visualización reutilizables
|
|-- requirements.txt
|-- README.md
'-- .gitignore
```
