Radiografía de Steam: características de publicación y recepción de videojuegos (2014 a 2024)

Proyecto de la asignatura **EIN092B Visualización** (2026-II). Avance 1: Formulación del proyecto.

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
- Población: títulos publicados entre 2014 y 2024, excluyendo contenido que no sea un juego (software,
  bandas sonoras, videos), y aplicando un umbral mínimo de reseñas para asegurar robustez en los indicadores de
  recepción.
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

La versión actual contiene aproximadamente 140.000 juegos (139.556 registros en la copia de Hugging Face). La
cifra exacta varía según la fecha de extracción.

Cómo obtener los datos

El archivo es demasiado pesado para versionarlo directamente en el repositorio, por lo que no se incluye en
`data/raw/`. Para reproducir el proyecto:

1. Descargar `games.csv` desde Hugging Face o Kaggle usando cualquiera de los enlaces anteriores.
2. Colocar el archivo en `data/raw/games.csv`.
3. Ejecutar el notebook `notebooks/01_exploracion.ipynb`, que valida la carga y describe la estructura.

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

A partir de estas variables se pueden derivar indicadores como la proporción de reseñas positivas
(positivas / (positivas + negativas)) y el número de idiomas soportados.

Estructura general del repositorio

```
proyecto-visualizacion/
|
|-- data/
|   |-- raw/          datos originales sin modificar (no versionados)
|   '-- processed/    datos generados tras limpieza y transformación
|
|-- notebooks/
|   '-- 01_exploracion.ipynb
|
|-- src/              funciones y código reutilizable
|-- figures/          gráficos y recursos visuales
|-- app/              aplicación o dashboard final
|-- docs/             documentación extendida del proyecto
|-- README.md
'-- .gitignore
```
