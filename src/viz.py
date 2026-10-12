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


TEXTO = "#1B2838"        # titulos y titulos de ejes (contraste alto sobre blanco)
TEXTO_SUAVE = "#3D4B59"  # etiquetas de las marcas de los ejes
LINEA_EJE = "#8A99A8"
GRILLA = "#E3E8EE"


def _layout_base(fig: go.Figure, titulo: str) -> go.Figure:
    """Aplica un estilo consistente y legible a cada figura.

    Cada figura fija su propio fondo blanco y colores de texto oscuros. La
    aplicacion las dibuja con theme=None, de modo que este estilo se mantiene
    igual aunque el navegador o Streamlit esten en modo oscuro. Asi los titulos
    de los ejes nunca quedan con un color parecido al del fondo.
    """
    fig.update_layout(
        template="plotly_white",
        title=dict(text=f"<b>{titulo}</b>", font=dict(size=18, color=TEXTO),
                   x=0.0, xanchor="left"),
        font=dict(family="Calibri, Arial, sans-serif", size=13, color=TEXTO),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=70, r=30, t=70, b=60),
        colorway=SEQ,
        hoverlabel=dict(bgcolor="white", font_color=TEXTO, bordercolor=LINEA_EJE),
        legend=dict(font=dict(color=TEXTO)),
        separators=",.",  # coma decimal y punto de miles, como se usa en Chile
    )
    estilo_ejes = dict(
        title_font=dict(size=14, color=TEXTO),
        tickfont=dict(size=12, color=TEXTO_SUAVE),
        linecolor=LINEA_EJE, showline=True, zeroline=False,
    )
    fig.update_xaxes(showgrid=False, **estilo_ejes)
    fig.update_yaxes(showgrid=True, gridcolor=GRILLA, **estilo_ejes)
    return fig


def releases_por_anio(df: pd.DataFrame) -> go.Figure:
    """Barras con el numero de lanzamientos por anio (contexto temporal)."""
    conteo = df.groupby("anio").size().reset_index(name="juegos")
    fig = px.bar(conteo, x="anio", y="juegos",
                 labels={"anio": ET["anio"], "juegos": "Número de juegos"})
    fig.update_traces(marker_color=C["deep"])
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(tickformat=",d")
    return _layout_base(fig, "Lanzamientos por año en el periodo analizado")


def distribucion_y(df: pd.DataFrame) -> go.Figure:
    """Histograma de la proporcion de resenas positivas (variable objetivo Y)."""
    datos = df.dropna(subset=["pct_positivas"])
    fig = px.histogram(datos, x="pct_positivas", nbins=40,
                       labels={"pct_positivas": ET["pct_positivas"]})
    fig.update_traces(marker_color=C["steam"], marker_line_color=C["deep"],
                      marker_line_width=0.5)
    mediana = datos["pct_positivas"].median()
    fig.add_vline(x=mediana, line_dash="dash", line_color=C["ambar"],
                  annotation_text=f"Mediana: {mediana * 100:.0f} %",
                  annotation_position="top left")
    fig.update_layout(yaxis_title="Número de juegos")
    fig.update_xaxes(tickformat=".0%")
    fig.update_yaxes(tickformat=",d")
    return _layout_base(fig, "Distribución de la proporción de reseñas positivas (Y)")


def _vista_inicial_precio(precios: pd.Series) -> float:
    """Limite derecho de la vista inicial del eje de precio.

    Todos los juegos se dibujan, pero la vista parte en el percentil 99 para que
    la mayoria de los datos sea legible. Con doble clic sobre el grafico (o el
    boton de autoescala) se ve el rango completo, hasta el precio maximo.
    """
    return float(precios.quantile(0.99)) * 1.1 if len(precios) else 100.0


def distribucion_precio(df: pd.DataFrame, log_y: bool = True) -> go.Figure:
    """Histograma de precios con barras de 1 USD y eje vertical opcionalmente logaritmico."""
    datos = df.dropna(subset=["precio"])
    fig = px.histogram(datos, x="precio", labels={"precio": ET["precio"]})
    fig.update_traces(marker_color=C["deep"], xbins=dict(start=0, size=1))
    fig.update_layout(yaxis_title="Número de juegos")
    fig.update_xaxes(range=[0, _vista_inicial_precio(datos["precio"])])
    if log_y:
        fig.update_yaxes(type="log")
    return _layout_base(fig, "Distribución de precios")


def explotar_generos(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve una fila por cada par (juego, genero).

    En el dataset la lista de generos viene casi siempre en orden alfabetico, por
    lo que el primer genero listado no representa el genero dominante del juego.
    Por eso el analisis por genero es multietiqueta: cada juego cuenta en todos
    los generos que declara.
    """
    datos = df.copy()
    datos["genero"] = datos["generos"].str.split(",")
    datos = datos.explode("genero")
    datos["genero"] = datos["genero"].str.strip()
    return datos[datos["genero"].notna() & (datos["genero"] != "")]


def frecuencia_generos(df: pd.DataFrame, top: int = 12) -> go.Figure:
    """Barras horizontales con los generos mas frecuentes (multietiqueta)."""
    conteo = (explotar_generos(df)["genero"].value_counts()
              .head(top).sort_values())
    fig = px.bar(x=conteo.values, y=conteo.index, orientation="h",
                 labels={"x": "Número de juegos que declaran el género",
                         "y": "Género"})
    fig.update_traces(marker_color=C["deep"])
    fig.update_xaxes(tickformat=",d")
    return _layout_base(fig, f"Géneros más frecuentes (top {top}, multietiqueta)")


def recepcion_por_genero(df: pd.DataFrame, top: int = 10) -> go.Figure:
    """Boxplot de la proporcion de positivas por genero (comparacion de grupos)."""
    datos = explotar_generos(df.dropna(subset=["pct_positivas"]))
    generos_top = datos["genero"].value_counts().head(top).index
    datos = datos[datos["genero"].isin(generos_top)]
    orden = (datos.groupby("genero")["pct_positivas"]
             .median().sort_values(ascending=False).index)
    fig = px.box(datos, x="genero", y="pct_positivas",
                 category_orders={"genero": list(orden)},
                 labels={"genero": "Género",
                         "pct_positivas": ET["pct_positivas"]})
    fig.update_traces(marker_color=C["steam"], line_color=C["deep"])
    fig.update_yaxes(tickformat=".0%")
    return _layout_base(fig, f"Recepción por género ({len(orden)} géneros con más juegos)")


# Tramos usados para resumir relaciones con medianas robustas
TRAMOS_PRECIO = [-0.01, 0.0, 2.0, 5.0, 10.0, 15.0, 20.0, 30.0, 40.0, 60.0, 100.0, np.inf]
ETIQUETAS_PRECIO = ["Gratis", "0 a 2", "2 a 5", "5 a 10", "10 a 15", "15 a 20",
                    "20 a 30", "30 a 40", "40 a 60", "60 a 100", "Más de 100"]
TRAMOS_IDIOMAS = [0, 1, 3, 6, 12, 20, 28, 29, np.inf]
ETIQUETAS_IDIOMAS = ["1", "2 a 3", "4 a 6", "7 a 12", "13 a 20", "21 a 28",
                     "29", "Más de 29"]
# Tramos que corresponden a declaraciones marcadas en bloque: los 29 idiomas
# principales de Steam o todos los idiomas que permite la tienda.
TRAMOS_EN_BLOQUE = {"29", "Más de 29"}


def mediana_por_tramo_precio(df: pd.DataFrame) -> pd.DataFrame:
    """Mediana de recepcion por tramo de precio, con el numero de juegos por tramo."""
    datos = df.dropna(subset=["precio", "pct_positivas"])
    tramo = pd.cut(datos["precio"], TRAMOS_PRECIO, labels=ETIQUETAS_PRECIO)
    return (datos.groupby(tramo, observed=True)
            .agg(precio=("precio", "median"),
                 pct_positivas=("pct_positivas", "median"),
                 juegos=("pct_positivas", "size"))
            .reset_index(names="tramo"))


def precio_vs_recepcion(df: pd.DataFrame, con_tendencia: bool = True) -> go.Figure:
    """Dispersion de precio contra recepcion (relacion entre X e Y).

    Se dibujan todos los juegos con resenas. El tamanio del punto codifica el
    volumen de resenas. Como tendencia se usa la mediana por tramo de precio en
    lugar de una recta: una regresion lineal sugeriria una relacion creciente que
    los datos no muestran en los precios altos.
    """
    datos = df.dropna(subset=["precio", "pct_positivas", "total_resenas"])
    fig = px.scatter(
        datos, x="precio", y="pct_positivas", size="total_resenas",
        size_max=22, opacity=0.35, render_mode="webgl",
        labels={"precio": ET["precio"], "pct_positivas": ET["pct_positivas"],
                "total_resenas": ET["total_resenas"]},
    )
    fig.update_traces(marker=dict(color=C["deep"]), name="Juegos")
    if con_tendencia:
        med = mediana_por_tramo_precio(datos)
        fig.add_trace(go.Scatter(
            x=med["precio"], y=med["pct_positivas"], mode="lines+markers",
            name="Mediana por tramo de precio",
            line=dict(color=C["ambar"], width=3), marker=dict(size=8),
            customdata=np.stack([med["tramo"].astype(str), med["juegos"]], axis=1),
            hovertemplate="Tramo %{customdata[0]} USD<br>Recepción mediana "
                          "%{y:.0%}<br>%{customdata[1]} juegos<extra></extra>",
        ))
        fig.update_layout(legend=dict(orientation="h", y=-0.25, x=0))
    fig.update_xaxes(range=[-1, _vista_inicial_precio(datos["precio"])])
    fig.update_yaxes(tickformat=".0%")
    return _layout_base(fig, "Precio frente a recepción")


def recepcion_por_comunidad(df: pd.DataFrame) -> go.Figure:
    """Compara la recepcion entre juegos con y sin funcionalidades comunitarias."""
    datos = df.dropna(subset=["pct_positivas"]).copy()
    if "comunidad" not in datos.columns:
        datos["comunidad"] = False
    datos["grupo"] = np.where(datos["comunidad"],
                              "Con comunidad", "Sin comunidad")
    fig = px.violin(datos, x="grupo", y="pct_positivas", box=True, points=False,
                    color="grupo",
                    category_orders={"grupo": ["Sin comunidad", "Con comunidad"]},
                    color_discrete_map={"Con comunidad": C["deep"],
                                        "Sin comunidad": C["ice"]},
                    labels={"grupo": "Multijugador o Steam Workshop",
                            "pct_positivas": ET["pct_positivas"]})
    # spanmode="hard" evita que la curva se extienda fuera del rango 0 a 100 %
    fig.update_traces(spanmode="hard")
    fig.update_layout(showlegend=False)
    fig.update_yaxes(tickformat=".0%")
    return _layout_base(fig, "Recepción según comunidad")


def popularidad_por_idiomas(df: pd.DataFrame) -> pd.DataFrame:
    """Mediana de resenas por tramo de idiomas, con el numero de juegos por tramo."""
    datos = df.dropna(subset=["n_idiomas", "total_resenas"])
    tramo = pd.cut(datos["n_idiomas"], TRAMOS_IDIOMAS, labels=ETIQUETAS_IDIOMAS)
    resumen = (datos.groupby(tramo, observed=True)["total_resenas"]
               .agg(mediana="median", juegos="size").reset_index(names="tramo"))
    # Redondeo hacia arriba en los medios (44,5 pasa a 45) para que el grafico y
    # el texto de interpretacion muestren exactamente la misma cifra.
    resumen["mediana"] = np.floor(resumen["mediana"] + 0.5)
    return resumen


def idiomas_vs_popularidad(df: pd.DataFrame) -> go.Figure:
    """Mediana de resenas por tramo de idiomas soportados (popularidad).

    Se agrupa por tramos porque los valores altos tienen pocos juegos y sus
    medianas individuales serian inestables. Los tramos "29" y "Mas de 29" se
    destacan en otro color porque reunen declaraciones marcadas en bloque.
    """
    resumen = popularidad_por_idiomas(df)
    colores = [C["ambar"] if t in TRAMOS_EN_BLOQUE else C["deep"]
               for t in resumen["tramo"].astype(str)]
    fig = go.Figure(go.Bar(
        x=resumen["tramo"].astype(str), y=resumen["mediana"],
        marker_color=colores, text=resumen["mediana"],
        texttemplate="%{text:.0f}", textposition="outside", textfont=dict(color=TEXTO),
        customdata=resumen["juegos"],
        hovertemplate="%{x} idiomas<br>Mediana de reseñas %{y:.0f}"
                      "<br>%{customdata:,} juegos<extra></extra>",
    ))
    fig.update_layout(xaxis_title=ET["n_idiomas"], yaxis_title="Mediana de reseñas")
    fig.update_yaxes(rangemode="tozero")
    return _layout_base(fig, "Popularidad según idiomas soportados")


def evolucion_recepcion(df: pd.DataFrame) -> go.Figure:
    """Serie temporal de la recepcion mediana por anio de lanzamiento (T)."""
    datos = df.dropna(subset=["pct_positivas", "anio"])
    resumen = (datos.groupby("anio")["pct_positivas"]
               .median().reset_index())
    fig = px.line(resumen, x="anio", y="pct_positivas", markers=True,
                  labels={"anio": ET["anio"],
                          "pct_positivas": "Mediana de reseñas positivas"})
    fig.update_traces(line_color=C["deep"], marker_color=C["ambar"],
                      line_width=2.5, marker_size=8)
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(range=[0, 1], tickformat=".0%")
    return _layout_base(fig, "Evolución de la recepción por año de lanzamiento")


# Etiquetas breves para la matriz de correlacion (los nombres largos se cortan)
ETIQUETAS_CORTAS = {
    "pct_positivas": "Recepción",
    "precio": "Precio",
    "total_resenas": "Total de reseñas",
    "n_idiomas": "Idiomas",
    "playtime_mediano": "Tiempo de juego",
    "n_sistemas": "Sistemas operativos",
}


def matriz_correlacion(df: pd.DataFrame) -> go.Figure:
    """Mapa de calor de correlaciones de Spearman entre las variables numericas clave."""
    columnas = [c for c in ETIQUETAS_CORTAS if c in df.columns]
    corr = df[columnas].corr(method="spearman")
    etiquetas = [ETIQUETAS_CORTAS[c] for c in columnas]
    fig = go.Figure(data=go.Heatmap(
        z=corr.values, x=etiquetas, y=etiquetas,
        colorscale="RdBu", zmid=0, zmin=-1, zmax=1,
        texttemplate="%{z:.2f}", textfont=dict(size=13),
        hovertemplate="%{y} y %{x}: %{z:.2f}<extra></extra>",
        colorbar=dict(title=dict(text="Spearman", font=dict(color=TEXTO)),
                      tickfont=dict(color=TEXTO_SUAVE)),
    ))
    fig.update_xaxes(tickangle=0, showline=False)
    fig.update_yaxes(autorange="reversed", showline=False, showgrid=False)
    fig = _layout_base(fig, "Correlación de Spearman entre variables numéricas")
    fig.update_layout(height=480)
    return fig


# ---------------------------------------------------------------------------
# Informacion complementaria: tiempo de juego e idiomas por subgrupos
# ---------------------------------------------------------------------------

# Minimo de juegos para considerar estable la mediana de un tramo
MIN_JUEGOS_TRAMO = 30


def con_tiempo_registrado(df: pd.DataFrame) -> pd.DataFrame:
    """Juegos con tiempo de juego registrado (mediano mayor que cero).

    La fuente solo registra el tiempo de juego para una parte de los juegos, en
    su mayoria los mas populares. Los analisis de tiempo se limitan a ese
    subgrupo y deben leerse como informacion sobre juegos con mas audiencia.
    """
    return df[df["playtime_mediano"] > 0].assign(
        horas=lambda d: d["playtime_mediano"] / 60
    )


def tiempo_por_tramo_precio(df: pd.DataFrame) -> go.Figure:
    """Horas medianas de juego por tramo de precio (solo juegos con registro)."""
    datos = con_tiempo_registrado(df)
    tramo = pd.cut(datos["precio"], TRAMOS_PRECIO, labels=ETIQUETAS_PRECIO)
    resumen = (datos.groupby(tramo, observed=True)["horas"]
               .agg(mediana="median", juegos="size").reset_index(names="tramo"))
    # Los tramos con menos de MIN_JUEGOS_TRAMO juegos se muestran en gris: no se
    # eliminan, pero su mediana es demasiado inestable para interpretarla.
    pequeno = resumen["juegos"] < MIN_JUEGOS_TRAMO
    fig = go.Figure(go.Bar(
        x=resumen["tramo"].astype(str), y=resumen["mediana"],
        marker_color=[C["ice"] if p else C["deep"] for p in pequeno],
        text=resumen["mediana"],
        texttemplate="%{text:.1f} h", textposition="outside", textfont=dict(color=TEXTO),
        customdata=resumen["juegos"],
        hovertemplate="Tramo %{x} USD<br>%{y:.1f} horas medianas"
                      "<br>%{customdata:,} juegos<extra></extra>",
    ))
    fig.update_layout(xaxis_title=ET["precio"], yaxis_title="Horas medianas de juego")
    fig.update_yaxes(range=[0, float(resumen["mediana"].max()) * 1.18])
    titulo = "Tiempo de juego según precio"
    if pequeno.any():
        titulo += f"<br><sup>En gris: tramos con menos de {MIN_JUEGOS_TRAMO} juegos</sup>"
    return _layout_base(fig, titulo)


def tiempo_por_genero(df: pd.DataFrame, top: int = 12) -> go.Figure:
    """Horas medianas de juego por genero (multietiqueta, solo juegos con registro)."""
    datos = explotar_generos(con_tiempo_registrado(df))
    generos_top = datos["genero"].value_counts().head(top).index
    resumen = (datos[datos["genero"].isin(generos_top)]
               .groupby("genero")["horas"].agg(mediana="median", juegos="size")
               .sort_values("mediana").reset_index())
    fig = go.Figure(go.Bar(
        x=resumen["mediana"], y=resumen["genero"], orientation="h",
        marker_color=C["deep"], text=resumen["mediana"],
        texttemplate="%{text:.1f} h", textposition="outside", textfont=dict(color=TEXTO),
        customdata=resumen["juegos"],
        hovertemplate="%{y}<br>%{x:.1f} horas medianas<br>%{customdata:,} juegos"
                      "<extra></extra>",
    ))
    fig.update_layout(xaxis_title="Horas medianas de juego", yaxis_title="Género")
    fig.update_xaxes(range=[0, float(resumen["mediana"].max()) * 1.25])
    return _layout_base(fig, "Tiempo de juego por género")


def explotar_idiomas(df: pd.DataFrame) -> pd.DataFrame:
    """Una fila por cada par (juego, idioma), excluyendo declaraciones en bloque."""
    datos = df[~df["idiomas_atipico"].fillna(False)]
    datos = datos[["lista_idiomas", "total_resenas", "pct_positivas"]].explode("lista_idiomas")
    return datos.dropna(subset=["lista_idiomas"]).rename(columns={"lista_idiomas": "idioma"})


def idiomas_mas_frecuentes(df: pd.DataFrame, top: int = 15,
                           destacar: str | None = None) -> go.Figure:
    """Porcentaje de juegos que soporta cada idioma (sin declaraciones en bloque)."""
    base = df[~df["idiomas_atipico"].fillna(False)]
    n = int((base["lista_idiomas"].map(len) > 0).sum())
    share = (explotar_idiomas(df)["idioma"].value_counts().head(top) / max(n, 1)).sort_values()
    colores = [C["ambar"] if i == destacar else C["deep"] for i in share.index]
    fig = go.Figure(go.Bar(
        x=share.values, y=share.index, orientation="h", marker_color=colores,
        text=share.values, texttemplate="%{text:.0%}", textposition="outside",
        textfont=dict(color=TEXTO),
        hovertemplate="%{y}<br>%{x:.1%} de los juegos<extra></extra>",
    ))
    fig.update_layout(xaxis_title="Porcentaje de juegos que soporta el idioma",
                      yaxis_title="Idioma")
    fig.update_xaxes(tickformat=".0%", range=[0, min(1.0, float(share.max()) * 1.12)])
    fig.update_layout(height=520)
    return _layout_base(fig, f"Idiomas más soportados (top {top})")


def comparar_idioma(df: pd.DataFrame, idioma: str) -> dict:
    """Compara juegos que soportan un idioma con los que no lo soportan.

    Devuelve el numero de juegos de cada grupo, su mediana de resenas
    (popularidad) y su mediana de resenas positivas (recepcion). Se excluyen las
    declaraciones en bloque, porque marcarian todos los idiomas a la vez.
    """
    base = df[~df["idiomas_atipico"].fillna(False) & (df["lista_idiomas"].map(len) > 0)]
    tiene = base["lista_idiomas"].map(lambda lista: idioma in lista)
    con, sin = base[tiene], base[~tiene]
    return {
        "juegos_con": len(con), "juegos_sin": len(sin),
        "resenas_con": con["total_resenas"].median(), "resenas_sin": sin["total_resenas"].median(),
        "recepcion_con": con["pct_positivas"].median(), "recepcion_sin": sin["pct_positivas"].median(),
    }


TRAMOS_GENEROS = [0, 1, 2, 3, 5, 8, np.inf]
ETIQUETAS_GENEROS = ["1", "2", "3", "4 a 5", "6 a 8", "Más de 8"]


def recepcion_por_n_generos(df: pd.DataFrame) -> go.Figure:
    """Recepcion mediana segun el numero de generos que declara cada juego."""
    datos = df.dropna(subset=["n_generos", "pct_positivas"])
    tramo = pd.cut(datos["n_generos"], TRAMOS_GENEROS, labels=ETIQUETAS_GENEROS)
    resumen = (datos.groupby(tramo, observed=True)["pct_positivas"]
               .agg(mediana="median", juegos="size").reset_index(names="tramo"))
    fig = go.Figure(go.Bar(
        x=resumen["tramo"].astype(str), y=resumen["mediana"], marker_color=C["deep"],
        text=resumen["mediana"], texttemplate="%{text:.0%}", textposition="outside",
        textfont=dict(color=TEXTO), customdata=resumen["juegos"],
        hovertemplate="%{x} géneros<br>Recepción mediana %{y:.0%}"
                      "<br>%{customdata:,} juegos<extra></extra>",
    ))
    fig.update_layout(xaxis_title=ET["n_generos"],
                      yaxis_title="Mediana de reseñas positivas")
    fig.update_yaxes(tickformat=".0%", range=[0, 1])
    return _layout_base(fig, "Recepción según número de géneros declarados")


def recepcion_por_tramo_precio(df: pd.DataFrame) -> go.Figure:
    """Recepcion mediana por tramo de precio, con todos los tramos visibles.

    Complementa la dispersion: alli la vista inicial se concentra en los precios
    habituales, mientras que aqui cada tramo (hasta "Mas de 100") ocupa el mismo
    espacio, lo que permite ver la caida de la recepcion en los precios altos.
    """
    resumen = mediana_por_tramo_precio(df)
    pequeno = resumen["juegos"] < MIN_JUEGOS_TRAMO
    # Solo se rotulan los puntos clave (gratis, maximo y minimo) para no saturar
    # el grafico; el resto se lee en el eje y al pasar el cursor.
    clave = {0, int(resumen["pct_positivas"].idxmax()), int(resumen["pct_positivas"].idxmin())} \
        if len(resumen) else set()
    etiquetas = [f"{v * 100:.0f} %" if i in clave else ""
                 for i, v in enumerate(resumen["pct_positivas"])]
    fig = go.Figure(go.Scatter(
        x=resumen["tramo"].astype(str), y=resumen["pct_positivas"],
        mode="lines+markers+text", line=dict(color=C["deep"], width=3),
        marker=dict(size=10, color=[C["ice"] if p else C["ambar"] for p in pequeno],
                    line=dict(color=C["deep"], width=1.5)),
        text=etiquetas, textposition="top center", textfont=dict(color=TEXTO, size=13),
        customdata=resumen["juegos"],
        hovertemplate="Tramo %{x} USD<br>Recepción mediana %{y:.0%}"
                      "<br>%{customdata:,} juegos<extra></extra>",
    ))
    fig.update_layout(xaxis_title="Tramo de precio (USD)",
                      yaxis_title="Mediana de reseñas positivas")
    piso = max(0.0, float(resumen["pct_positivas"].min()) - 0.1) if len(resumen) else 0.0
    fig.update_yaxes(tickformat=".0%", range=[piso, 1.0])
    return _layout_base(fig, "Recepción mediana por tramo de precio")
