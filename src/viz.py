"""
Funciones de visualizacion reutilizables.

Cada funcion recibe un DataFrame ya limpio y devuelve una figura de Plotly.
Mantener la logica de los graficos separada de la aplicacion cumple dos
objetivos: permite probar las figuras sin levantar Streamlit y asegura que el
notebook y la aplicacion produzcan exactamente las mismas visualizaciones.

Todas las figuras comparten la paleta y las etiquetas definidas en config, de
modo que el producto visual se lee como un solo sistema.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from . import config

C = config.COLORES
SEQ = config.SECUENCIA_COLORES
ET = config.ETIQUETAS


def _layout_base(fig: go.Figure, titulo: str) -> go.Figure:
    """Aplica un estilo consistente a cada figura."""
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=18, color=C["navy"])),
        font=dict(family="Calibri, Arial, sans-serif", size=13, color=C["navy"]),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=60, r=30, t=60, b=50),
        colorway=SEQ,
    )
    fig.update_xaxes(showgrid=False, linecolor=C["ice"])
    fig.update_yaxes(showgrid=True, gridcolor="#E8EDF2")
    return fig


def releases_por_anio(df: pd.DataFrame) -> go.Figure:
    """Barras con el numero de lanzamientos por anio (contexto temporal)."""
    conteo = df.groupby("anio").size().reset_index(name="juegos")
    fig = px.bar(conteo, x="anio", y="juegos",
                 labels={"anio": ET["anio"], "juegos": "Numero de juegos"})
    fig.update_traces(marker_color=C["deep"])
    return _layout_base(fig, "Lanzamientos por anio en el periodo analizado")


def distribucion_y(df: pd.DataFrame) -> go.Figure:
    """Histograma de la proporcion de resenas positivas (variable objetivo Y)."""
    datos = df.dropna(subset=["pct_positivas"])
    fig = px.histogram(datos, x="pct_positivas", nbins=40,
                       labels={"pct_positivas": ET["pct_positivas"]})
    fig.update_traces(marker_color=C["steam"], marker_line_color=C["deep"],
                      marker_line_width=0.5)
    mediana = datos["pct_positivas"].median()
    fig.add_vline(x=mediana, line_dash="dash", line_color=C["ambar"],
                  annotation_text=f"Mediana: {mediana:.2f}",
                  annotation_position="top left")
    fig.update_layout(yaxis_title="Numero de juegos")
    return _layout_base(fig, "Distribucion de la proporcion de resenas positivas")


def distribucion_precio(df: pd.DataFrame, log_y: bool = True) -> go.Figure:
    """Histograma de precios, con opcion de eje vertical logaritmico."""
    datos = df.dropna(subset=["precio"])
    fig = px.histogram(datos, x="precio", nbins=50,
                       labels={"precio": ET["precio"]})
    fig.update_traces(marker_color=C["deep"])
    fig.update_layout(yaxis_title="Numero de juegos")
    if log_y:
        fig.update_yaxes(type="log")
    return _layout_base(fig, "Distribucion de precios")


def frecuencia_generos(df: pd.DataFrame, top: int = 12) -> go.Figure:
    """Barras horizontales con los generos principales mas frecuentes."""
    conteo = (df["genero_principal"].dropna().value_counts()
              .head(top).sort_values())
    fig = px.bar(x=conteo.values, y=conteo.index, orientation="h",
                 labels={"x": "Numero de juegos", "y": ET["genero_principal"]})
    fig.update_traces(marker_color=C["deep"])
    return _layout_base(fig, f"Generos principales mas frecuentes (top {top})")


def recepcion_por_genero(df: pd.DataFrame, top: int = 10) -> go.Figure:
    """Boxplot de la proporcion de positivas por genero (comparacion de grupos)."""
    datos = df.dropna(subset=["pct_positivas", "genero_principal"])
    generos_top = datos["genero_principal"].value_counts().head(top).index
    datos = datos[datos["genero_principal"].isin(generos_top)]
    orden = (datos.groupby("genero_principal")["pct_positivas"]
             .median().sort_values(ascending=False).index)
    fig = px.box(datos, x="genero_principal", y="pct_positivas",
                 category_orders={"genero_principal": list(orden)},
                 labels={"genero_principal": ET["genero_principal"],
                         "pct_positivas": ET["pct_positivas"]})
    fig.update_traces(marker_color=C["steam"], line_color=C["deep"])
    return _layout_base(fig, "Recepcion por genero principal")


def precio_vs_recepcion(df: pd.DataFrame, con_tendencia: bool = True) -> go.Figure:
    """Dispersion de precio contra recepcion (relacion entre X e Y).

    El tamanio del punto codifica el volumen de resenas, de modo que se puede
    distinguir a simple vista cuales puntos tienen respaldo de muchas resenas.
    """
    datos = df.dropna(subset=["precio", "pct_positivas", "total_resenas"]).copy()
    datos = datos[datos["precio"] <= 80]  # recorta precios atipicos para legibilidad
    args = dict(
        x="precio", y="pct_positivas", size="total_resenas",
        size_max=22, opacity=0.45,
        labels={"precio": ET["precio"], "pct_positivas": ET["pct_positivas"],
                "total_resenas": ET["total_resenas"]},
    )
    if con_tendencia:
        try:
            fig = px.scatter(datos, trendline="ols",
                             trendline_color_override=C["ambar"], **args)
        except Exception:
            fig = px.scatter(datos, **args)
    else:
        fig = px.scatter(datos, **args)
    fig.update_traces(marker=dict(color=C["deep"]),
                      selector=dict(mode="markers"))
    return _layout_base(fig, "Precio frente a recepcion")


def recepcion_por_comunidad(df: pd.DataFrame) -> go.Figure:
    """Compara la recepcion entre juegos con y sin funcionalidades comunitarias."""
    datos = df.dropna(subset=["pct_positivas"]).copy()
    if "comunidad" not in datos.columns:
        datos["comunidad"] = False
    datos["grupo"] = np.where(datos["comunidad"],
                              "Con comunidad", "Sin comunidad")
    fig = px.violin(datos, x="grupo", y="pct_positivas", box=True, points=False,
                    color="grupo",
                    color_discrete_map={"Con comunidad": C["deep"],
                                        "Sin comunidad": C["ice"]},
                    labels={"grupo": "Funcionalidades comunitarias",
                            "pct_positivas": ET["pct_positivas"]})
    fig.update_layout(showlegend=False)
    return _layout_base(fig, "Recepcion segun presencia de comunidad")


def idiomas_vs_popularidad(df: pd.DataFrame) -> go.Figure:
    """Relacion entre numero de idiomas y volumen de resenas (popularidad)."""
    datos = df.dropna(subset=["n_idiomas", "total_resenas"]).copy()
    datos = datos[datos["total_resenas"] > 0]
    resumen = (datos.groupby("n_idiomas")["total_resenas"]
               .median().reset_index())
    resumen = resumen[resumen["n_idiomas"] <= 30]
    fig = px.line(resumen, x="n_idiomas", y="total_resenas", markers=True,
                  labels={"n_idiomas": ET["n_idiomas"],
                          "total_resenas": "Mediana de resenas"})
    fig.update_traces(line_color=C["deep"], marker_color=C["ambar"])
    return _layout_base(fig, "Idiomas soportados frente a popularidad")


def evolucion_recepcion(df: pd.DataFrame) -> go.Figure:
    """Serie temporal de la recepcion mediana por anio de lanzamiento (T)."""
    datos = df.dropna(subset=["pct_positivas", "anio"])
    resumen = (datos.groupby("anio")["pct_positivas"]
               .median().reset_index())
    fig = px.line(resumen, x="anio", y="pct_positivas", markers=True,
                  labels={"anio": ET["anio"],
                          "pct_positivas": "Mediana de " + ET["pct_positivas"].lower()})
    fig.update_traces(line_color=C["deep"], marker_color=C["ambar"],
                      line_width=2.5)
    fig.update_yaxes(range=[0, 1])
    return _layout_base(fig, "Evolucion de la recepcion por anio de lanzamiento")


def matriz_correlacion(df: pd.DataFrame) -> go.Figure:
    """Mapa de calor de correlaciones entre las variables numericas clave."""
    columnas = [c for c in ["pct_positivas", "precio", "total_resenas",
                            "n_idiomas", "playtime_mediano", "n_sistemas"]
                if c in df.columns]
    corr = df[columnas].corr(method="spearman")
    etiquetas = [ET.get(c, c) for c in columnas]
    fig = go.Figure(data=go.Heatmap(
        z=corr.values, x=etiquetas, y=etiquetas,
        colorscale="RdBu", zmid=0, zmin=-1, zmax=1,
        text=np.round(corr.values, 2), texttemplate="%{text}",
        colorbar=dict(title="Spearman"),
    ))
    return _layout_base(fig, "Correlacion entre variables numericas")
