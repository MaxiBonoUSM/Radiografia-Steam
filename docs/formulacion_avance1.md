# Formulación del proyecto (Avance 1)

**Asignatura:** EIN092B Visualización, 2026-II
**Proyecto:** Radiografía de Steam: características de publicación y recepción de videojuegos (2014 a 2024)

Este documento desarrolla en detalle los elementos solicitados para el Avance 1. Sigue la lógica esperada por
la guía del curso: Problema, Pregunta, Datos, Análisis y Visualización.

## 1. Problema y motivación

Steam es la plataforma dominante de distribución de videojuegos para PC. Durante la última década, la cantidad
de títulos publicados por año creció de forma acelerada, alcanzando varios miles de lanzamientos anuales. Este
crecimiento produjo un mercado saturado en el que la visibilidad se concentra en un grupo reducido de juegos,
mientras la mayoría recibe muy pocas reseñas y poca atención.

Frente a ese escenario surge una pregunta natural: ¿qué características de un juego se asocian con una mejor
recepción por parte de los jugadores? La respuesta no es evidente, ya que intervienen múltiples factores como
el precio, el género, la localización de idiomas, el soporte multiplataforma, la presencia de funcionalidades
comunitarias y el momento del lanzamiento.

La motivación del proyecto es doble. En lo práctico, comprender estas relaciones apoya decisiones de estudios
independientes y analistas del sector sobre cómo publicar un título en un mercado competitivo. En lo
metodológico, se trata de un fenómeno con datos públicos y ricos en dimensiones numéricas, categóricas y
temporales, lo que lo hace idóneo para construir una narrativa visual durante el semestre.

## 2. Pregunta y alcance

### Pregunta principal

¿Cómo se relacionan las características de publicación y diseño de un videojuego en Steam (género, precio,
número de idiomas soportados, soporte multiplataforma y funcionalidades comunitarias) con su nivel de recepción
y compromiso de los jugadores, en los títulos publicados entre 2014 y 2024?

### Delimitación del alcance

Para responder al listado de preguntas orientadoras de la guía:

- **Fenómeno específico:** la recepción y el compromiso de los jugadores frente a las características de cada
  juego.
- **Decisión que se apoya:** qué atributos priorizar al publicar un juego en un mercado saturado.
- **Unidad de observación:** un videojuego publicado en Steam (un AppID).
- **Variable de interés principal:** la proporción de reseñas positivas, complementada con indicadores de
  compromiso y popularidad.
- **Periodo temporal:** juegos publicados entre 2014 y 2024.
- **Población y contexto:** catálogo de Steam, excluyendo software y contenido que no sea un juego, con un
  umbral mínimo de reseñas.
- **Información disponible:** las variables descritas en la sección de datos.
- **Aspectos fuera de alcance:** ventas monetarias reales, análisis del texto de las reseñas, comportamiento
  individual de jugadores y análisis geográfico detallado.

Un buen alcance para este proyecto es concreto, medible, visualizable y abordable con los datos disponibles.

## 3. Estructura X, Y y T

| Componente | Definición | Variables o forma concreta |
|---|---|---|
| **X** | Información disponible sobre cada juego | Género, precio, número de idiomas soportados, soporte de sistemas operativos, funcionalidades comunitarias (multijugador, Steam Workshop), presencia de DLC, mes o año de lanzamiento |
| **Y** | Objetivo o fenómeno de interés | Recepción (proporción de reseñas positivas), compromiso (tiempo de juego mediano), popularidad (volumen de reseñas) |
| **T** | Contexto temporal | Juegos publicados entre 2014 y 2024 |

Los tres componentes forman la pregunta del proyecto: se busca describir cómo se asocian las características de
un juego (X) con su recepción y compromiso (Y) dentro del periodo definido (T). El componente temporal se usa
para delimitar el análisis, no para realizar una predicción a futuro.

## 4. Dataset y narrativa inicial

**Fuente:** Steam Games Dataset, mantenido por Fronkon Games, generado con un scraper de código abierto
(licencia MIT) que consume la API oficial de Steam y complementa con SteamSpy.

- Enlaces: Hugging Face y Kaggle (ver README).
- Tamaño aproximado: 140.000 juegos (la cifra exacta varía según la fecha de extracción).
- Unidad: un juego por fila.
- Cobertura: catálogo publicado en Steam, con lanzamientos que abarcan varias décadas; el proyecto se centra en
  el periodo 2014 a 2024.

### Variables principales

- **Identificación:** AppID, nombre.
- **Temporal:** fecha de lanzamiento.
- **Numéricas:** precio, cantidad de DLC, reseñas positivas y negativas, recomendaciones, pico de usuarios
  concurrentes, puntaje Metacritic, tiempos de juego promedio y mediano.
- **Categóricas y de texto:** géneros, categorías, etiquetas, idiomas soportados, desarrolladores, publicadores.
- **Booleanas:** soporte para Windows, Mac y Linux.
- **Rangos:** estimación de propietarios por tramos.

### Indicadores derivados

- Proporción de reseñas positivas: positivas / (positivas + negativas).
- Número de idiomas soportados: conteo a partir del listado de idiomas.
- Indicador de funcionalidades comunitarias: presencia de multijugador o de Steam Workshop.

### Narrativa inicial

Los datos describen el catálogo de juegos publicados en Steam y su recepción acumulada. Permiten construir una
historia sobre cómo el mercado se ha llenado de títulos, qué géneros predominan, cómo se distribuyen los
precios y qué características tienden a acompañar a los juegos mejor valorados. La historia central que se busca
explorar es la relación entre las decisiones de publicación de un juego y la respuesta de los jugadores.

## 5. Coherencia y potencial visual

### Relación pregunta y datos

Cada elemento de la pregunta tiene respaldo directo en los datos. Las variables X existen como columnas o
pueden derivarse. La recepción y el compromiso (Y) se obtienen de las reseñas y de los tiempos de juego. El
periodo (T) se filtra con la fecha de lanzamiento. Por lo tanto, los datos contienen la información necesaria
para abordar la pregunta.

### Potencial visual

- **Temporal:** evolución del número de lanzamientos por año y de la proporción de reseñas positivas según año
  de lanzamiento.
- **Comparación entre grupos:** recepción y precio por género, o según la presencia de funcionalidades
  comunitarias.
- **Relaciones numéricas:** precio frente a recepción, tiempo de juego frente a recepción, número de idiomas
  frente a popularidad.
- **Distribuciones:** distribución de precios y de la proporción de reseñas positivas.
- **KPIs candidatos:** proporción mediana de reseñas positivas, porcentaje de juegos bien recibidos, tiempo de
  juego mediano por género.

### Limitaciones iniciales

- Los datos son un corte transversal. Las métricas acumuladas (reseñas, tiempo de juego) favorecen a los juegos
  más antiguos, por lo que conviene normalizar o controlar por año de lanzamiento.
- La estimación de propietarios se entrega en tramos amplios.
- La proporción de reseñas positivas es poco confiable en juegos con muy pocas reseñas, lo que justifica un
  umbral mínimo.
- Solo hay juegos publicados, lo que introduce un sesgo de supervivencia.
- No se dispone de ventas reales ni de información geográfica de los usuarios.
- Los géneros, categorías y etiquetas son campos con múltiples valores que requieren procesamiento.

## 6. Organización en GitHub

El repositorio sigue la estructura recomendada por la guía, con carpetas para datos, notebooks, código,
figuras, aplicación y documentación. El README inicial contiene el nombre del proyecto, integrantes,
descripción del problema, motivación, pregunta, alcance, fuente y descripción de los datos, y estructura del
repositorio. Los datos no se versionan y el README indica cómo obtenerlos.

## 7. Resultado esperado del avance

Al finalizar este avance el proyecto cuenta con una problemática identificada, una motivación clara, una
pregunta analítica concreta, un alcance razonable, una definición inicial de X, Y y T, un dataset identificado
y disponible, una narrativa inicial, una justificación de la relación entre pregunta y datos, una
identificación preliminar del potencial visual y un repositorio organizado. Esto constituye una base suficiente
para comenzar el Avance 2.
