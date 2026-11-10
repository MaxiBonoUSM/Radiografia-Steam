"""
Modelado predictivo del Avance 3.

Tarea: clasificacion binaria. Se predice si un juego quedara "destacado", es
decir, entre el 20 por ciento de juegos con mas resenas de su mismo anio de
lanzamiento, usando solo informacion disponible al momento de publicarlo.

Decisiones principales (justificadas en la presentacion):

- Objetivo relativo a la cohorte anual. Un umbral fijo de resenas (por ejemplo,
  100) mezcla calidad de publicacion con tiempo de exposicion: lo cumple el 77 %
  de los juegos de 2014 y solo el 11 % de los de 2024. Comparar cada juego con
  los de su propio anio elimina ese efecto y deja la prevalencia en 20 % todos
  los anios.
- Variables sin fuga de informacion. Solo entran caracteristicas que el juego
  tiene al publicarse: precio, idiomas, generos, sistemas operativos y
  funcionalidades declaradas. Se excluyen las que dependen del exito posterior
  (resenas, recomendaciones, propietarios, tiempo de juego, DLC, Steam Workshop,
  cromos de Steam y etiquetas de usuarios).
- Particion temporal. Se entrena con juegos de 2014 a 2022 y se evalua con los
  de 2023 y 2024, como ocurriria al usar el modelo con lanzamientos nuevos.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, average_precision_score, f1_score, precision_score,
    recall_score, roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Parametros del problema
CUANTIL_DESTACADO = 0.80          # el 20 % superior de su anio
ANIOS_ENTRENAMIENTO = (2014, 2022)
ANIOS_PRUEBA = (2023, 2024)
ANIOS_VALIDACION = [2019, 2020, 2021, 2022]   # validacion cruzada hacia adelante
SEMILLA = 42

# Idiomas especificos con mas presencia en el catalogo
IDIOMAS_CLAVE = [
    "English", "Simplified Chinese", "German", "French", "Japanese", "Russian",
    "Spanish - Spain", "Spanish - Latin America", "Korean", "Portuguese - Brazil",
    "Traditional Chinese", "Italian", "Polish",
]

# Funcionalidades declaradas por el desarrollador al publicar
CATEGORIAS_CLAVE = {
    "Multi-player": "multijugador",
    "Co-op": "cooperativo",
    "Steam Achievements": "logros_steam",
    "Steam Cloud": "steam_cloud",
    "Full controller support": "control_completo",
    "VR Only": "solo_vr",
    "Steam Leaderboards": "tablas_puntaje",
}

# Variables excluidas por depender del exito posterior al lanzamiento
EXCLUIDAS = {
    "Reseñas, recomendaciones, propietarios, pico de jugadores": "definen o reflejan el objetivo",
    "Tiempo de juego, Metacritic, puntaje de usuarios": "se miden después del lanzamiento",
    "DLC y Steam Workshop": "suelen agregarse cuando el juego ya tuvo éxito",
    "Cromos de Steam (Trading Cards)": "Valve los habilita según las ventas",
    "Etiquetas (Tags)": "las asignan los jugadores",
    "Descuento actual": "es una condición de hoy, no del lanzamiento",
}


def crear_objetivo(df: pd.DataFrame) -> pd.Series:
    """Marca como destacado al 20 % de juegos con mas resenas de su anio."""
    umbral = df.groupby("anio")["total_resenas"].transform(
        lambda s: s.quantile(CUANTIL_DESTACADO)
    )
    return (df["total_resenas"] >= umbral).astype(int)


def umbrales_por_anio(df: pd.DataFrame) -> pd.Series:
    """Numero minimo de resenas para quedar destacado en cada anio."""
    return df.groupby("anio")["total_resenas"].quantile(CUANTIL_DESTACADO)


def _tiene(serie_listas: pd.Series, valor: str) -> pd.Series:
    return serie_listas.map(lambda lista: int(valor in lista))


def construir_variables(df: pd.DataFrame, generos_modelo: list[str] | None = None):
    """Construye la matriz X con informacion disponible al lanzamiento.

    Devuelve (X, generos_modelo). La lista de generos se define con los datos de
    entrenamiento y se reutiliza tal cual en prueba, para que ambas matrices
    tengan las mismas columnas.
    """
    X = pd.DataFrame(index=df.index)

    # Precio
    X["precio"] = df["precio"].fillna(0)
    X["es_gratis"] = (X["precio"] == 0).astype(int)

    # Idiomas
    X["n_idiomas"] = df["n_idiomas"].fillna(0)
    X["idiomas_en_bloque"] = df["idiomas_atipico"].fillna(False).astype(int)
    X["n_idiomas_audio"] = df["n_idiomas_audio"].fillna(0)
    listas = df["lista_idiomas"]
    for idioma in IDIOMAS_CLAVE:
        X["idioma_" + idioma] = _tiene(listas, idioma)

    # Generos (multietiqueta)
    generos = df["generos"].fillna("").str.split(",").map(
        lambda gs: {g.strip() for g in gs if g.strip()}
    )
    if generos_modelo is None:
        conteo = pd.Series([g for gs in generos for g in gs]).value_counts()
        generos_modelo = conteo[conteo >= 200].index.tolist()
    for genero in generos_modelo:
        X["genero_" + genero] = generos.map(lambda gs, g=genero: int(g in gs))
    X["n_generos"] = df["n_generos"].fillna(0)

    # Plataformas y funcionalidades declaradas
    X["windows"] = df["windows"].astype(int)
    X["mac"] = df["mac"].astype(int)
    X["linux"] = df["linux"].astype(int)
    categorias = df["categorias"].fillna("")
    for original, nombre in CATEGORIAS_CLAVE.items():
        X[nombre] = categorias.str.contains(original, regex=False).astype(int)

    # Otros datos del lanzamiento
    X["edad_restringida"] = (df["edad_requerida"].fillna(0) > 0).astype(int)
    X["mes_lanzamiento"] = df["mes"].fillna(6)

    return X, generos_modelo


def particion_temporal(df: pd.DataFrame):
    """Mascaras booleanas de entrenamiento (2014 a 2022) y prueba (2023 y 2024)."""
    entrenamiento = df["anio"].between(*ANIOS_ENTRENAMIENTO)
    prueba = df["anio"].between(*ANIOS_PRUEBA)
    return entrenamiento, prueba


def pliegues_hacia_adelante(anios: pd.Series):
    """Validacion cruzada que respeta el orden temporal.

    En cada pliegue se entrena con todos los anios anteriores y se valida con
    el anio siguiente (2019, 2020, 2021 y 2022). Nunca se usa informacion de un
    anio posterior para predecir uno anterior.
    """
    for anio_val in ANIOS_VALIDACION:
        idx_ent = np.where(anios < anio_val)[0]
        idx_val = np.where(anios == anio_val)[0]
        yield idx_ent, idx_val


# Columnas numericas que la regresion logistica transforma con logaritmo
COLUMNAS_LOG = ["precio", "n_idiomas", "n_idiomas_audio", "n_generos"]


def transformar_para_lineal(X: pd.DataFrame) -> pd.DataFrame:
    """Aplica log(1 + x) a las variables muy asimetricas (solo modelo lineal)."""
    X = X.copy()
    for c in COLUMNAS_LOG:
        X[c] = np.log1p(X[c])
    return X


def modelo_logistico(C: float = 1.0) -> Pipeline:
    """Regresion logistica con escalado. El escalado se ajusta solo en entrenamiento."""
    return Pipeline([
        ("escalado", StandardScaler()),
        ("modelo", LogisticRegression(C=C, max_iter=2000)),
    ])


def modelo_lightgbm(**parametros):
    """Gradient boosting de arboles (LightGBM)."""
    from lightgbm import LGBMClassifier
    base = dict(n_estimators=400, learning_rate=0.05, num_leaves=31,
                min_child_samples=50, subsample=0.8, subsample_freq=1,
                colsample_bytree=0.8, random_state=SEMILLA, verbose=-1)
    base.update(parametros)
    return LGBMClassifier(**base)


def metricas(y_real, prob, umbral: float) -> dict:
    """Metricas de clasificacion para un umbral dado."""
    pred = (prob >= umbral).astype(int)
    return {
        "accuracy": accuracy_score(y_real, pred),
        "precision": precision_score(y_real, pred, zero_division=0),
        "recall": recall_score(y_real, pred),
        "f1": f1_score(y_real, pred),
        "roc_auc": roc_auc_score(y_real, prob),
        "ap": average_precision_score(y_real, prob),
    }


def umbral_optimo_f1(y_real, prob) -> float:
    """Umbral que maximiza F1, buscado sobre predicciones de validacion."""
    candidatos = np.linspace(0.05, 0.95, 181)
    puntajes = [f1_score(y_real, (prob >= u).astype(int)) for u in candidatos]
    return float(candidatos[int(np.argmax(puntajes))])


# Nombres legibles para los graficos de explicabilidad
_IDIOMAS_ES = {
    "English": "inglés", "Simplified Chinese": "chino simplificado", "German": "alemán",
    "French": "francés", "Japanese": "japonés", "Russian": "ruso",
    "Spanish - Spain": "español (España)", "Spanish - Latin America": "español (Latinoamérica)",
    "Korean": "coreano", "Portuguese - Brazil": "portugués (Brasil)",
    "Traditional Chinese": "chino tradicional", "Italian": "italiano", "Polish": "polaco",
}
_FIJAS = {
    "precio": "Precio (USD)", "es_gratis": "Es gratuito", "n_idiomas": "N.º de idiomas",
    "idiomas_en_bloque": "Idiomas marcados en bloque", "n_idiomas_audio": "N.º de idiomas con audio",
    "n_generos": "N.º de géneros", "windows": "Soporta Windows", "mac": "Soporta macOS",
    "linux": "Soporta Linux", "multijugador": "Multijugador", "cooperativo": "Cooperativo",
    "logros_steam": "Logros de Steam", "steam_cloud": "Steam Cloud",
    "control_completo": "Soporte completo de control", "solo_vr": "Solo VR",
    "tablas_puntaje": "Tablas de puntaje", "edad_restringida": "Edad restringida",
    "mes_lanzamiento": "Mes de lanzamiento",
}


def etiqueta(columna: str) -> str:
    """Nombre legible de una variable del modelo."""
    if columna in _FIJAS:
        return _FIJAS[columna]
    if columna.startswith("idioma_"):
        return "Idioma: " + _IDIOMAS_ES.get(columna[7:], columna[7:])
    if columna.startswith("genero_"):
        return "Género: " + columna[7:]
    return columna
