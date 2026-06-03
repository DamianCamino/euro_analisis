import os
from pathlib import Path

import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go

from translations import t

# división por objetos

class Relacion:
    def __init__(self, iso2, nombre, valor):
        self.iso2 = iso2
        self.nombre = nombre
        self.valor = valor


class Analisis:
    def __init__(self, total, relaciones):
        self.total = total
        self.relaciones = relaciones


class Pais:
    def __init__(self, iso2, nombre, lat, lon,
                 recepcion, emision):

        self.iso2 = iso2
        self.nombre = nombre
        self.lat = lat
        self.lon = lon
        self.recepcion = recepcion
        self.emision = emision


# relación de coordenadas para el mapa con nombres en inglés (se traducen dinámicamente)
coords = {
"AT": ("Austria",47.51,14.55),
"BE": ("Belgium",50.85,4.35),
"BG": ("Bulgaria",42.69,23.32),
"CY": ("Cyprus",35.12,33.43),
"CZ": ("Czech Republic",50.07,14.43),
"CZ_SK": ("Czech Republic",50.07,14.43),  
"DE": ("Germany",51.16,10.45),
"DK": ("Denmark",55.67,12.56),
"EE": ("Estonia",59.43,24.75),
"EL": ("Greece",37.98,23.72),
"ES": ("Spain",40.46,-3.74),
"FI": ("Finland",60.17,24.93),
"FR": ("France",48.85,2.35),
"HR": ("Croatia",45.1,15.2),
"HU": ("Hungary",47.16,19.50),
"IE": ("Ireland",53.34,-6.26),
"IT": ("Italy",41.87,12.56),
"LT": ("Lithuania",54.68,25.27),
"LU": ("Luxembourg",49.61,6.13),
"LV": ("Latvia",56.94,24.10),
"MT": ("Malta",35.89,14.51),
"NL": ("Netherlands",52.13,5.29),
"PL": ("Poland",52.23,21.01),
"PT": ("Portugal",38.72,-9.13),
"RO": ("Romania",45.94,24.96),
"SE": ("Sweden",59.32,18.06),
"SI": ("Slovenia",46.05,14.50),
"SK": ("Slovakia",48.14,17.10),
}


# los datos han sido sacados de migr_imm1ctz, del portal de datos de Eurostat
# para facilidad de uso, los divido en recepción, según los valores citizen y geo del repositorio original
#
BASE_DIR = Path(__file__).resolve().parent

df_recep = pd.read_csv(BASE_DIR / "recepcion_nuevo.csv")
df_emi = pd.read_csv(BASE_DIR / "emigracion_nuevo.csv")




def construir_recepcion(iso2):

    sub = df_recep[df_recep["Código Destino"] == iso2]

    total = sub["Cantidad"].sum()

    top = sub.sort_values(
        "Cantidad", ascending=False
    ).head(3)

    relaciones = [
        Relacion(
            r["Código Origen"],
            r["País Origen"],
            int(r["Cantidad"])
        )
        for _, r in top.iterrows()
    ]

    return Analisis(int(total), relaciones)


def construir_emision(iso2):

    sub = df_emi[df_emi["Código Origen"] == iso2]

    total = sub["Cantidad"].sum()

    top = sub.sort_values(
        "Cantidad", ascending=False
    ).head(3)

    relaciones = [
        Relacion(
            r["Código Destino"],
            r["País Destino"],
            int(r["Cantidad"])
        )
        for _, r in top.iterrows()
    ]

    return Analisis(int(total), relaciones)



paises = {}

for iso2,(nombre,lat,lon) in coords.items():

    paises[iso2] = Pais(
        iso2,
        nombre,
        lat,
        lon,
        construir_recepcion(iso2),
        construir_emision(iso2)
    )

print(f"{t('total_countries')}: {len(paises)}")
for iso, p in paises.items():
    if p.recepcion.relaciones or p.emision.relaciones:
        print(f"{iso}: {len(p.recepcion.relaciones)} rec, {len(p.emision.relaciones)} emi")


def mapa_base(lang="es"):

    lats,lons,texts,isos=[],[],[],[]

    for iso,p in paises.items():
        lats.append(p.lat)
        lons.append(p.lon)
        # COMMENTED OUT: Removes name tags next to points
        # texts.append(t(f"countries.{iso}", lang))
        isos.append(iso)

    fig = go.Figure(go.Scattergeo(
        lat=lats,
        lon=lons,
        # COMMENTED OUT: Removes hover behavior and text display
        # text=texts,
        customdata=isos,
        # COMMENTED OUT: Changed from "markers+text" to "markers" to disable text labels
        # mode="markers+text",
        mode="markers",
        # COMMENTED OUT: No longer needed
        # textposition="top center",
        marker=dict(size=8,color="grey"),
        # ADDED: Disable hover information
        hoverinfo="skip"
    ))

    fig.update_geos(scope="europe", showcountries=True)

    return fig


def agregar_flechas(fig, pais, lang="es"):

    # Get all immigration and emigration countries for this pais
    immigration_isos = {r.iso2 for r in pais.recepcion.relaciones}
    emigration_isos = {r.iso2 for r in pais.emision.relaciones}
    
    # Find countries that are in BOTH immigration and emigration (bidirectional)
    bidirectional_isos = immigration_isos & emigration_isos

    # RECEPCION (Immigration - Orange lines)
    for r in pais.recepcion.relaciones:
        if r.iso2 in paises:
            origen = paises[r.iso2]
            
            # Skip if this is a bidirectional flow (will be drawn as purple)
            if r.iso2 in bidirectional_isos:
                continue

            fig.add_trace(go.Scattergeo(
                lat=[origen.lat, pais.lat],
                lon=[origen.lon, pais.lon],
                mode="lines",
                line=dict(color="orange", width=2),
                showlegend=False,
                hoverinfo="skip"
            ))

    # EMISION (Emigration - Blue lines)
    for r in pais.emision.relaciones:
        if r.iso2 in paises:
            destino = paises[r.iso2]
            
            # Skip if this is a bidirectional flow (will be drawn as purple)
            if r.iso2 in bidirectional_isos:
                continue
                
            dx = destino.lon - pais.lon
            dy = destino.lat - pais.lat
            if abs(dx) > abs(dy):
                arrow_symbol = "arrow-right" if dx > 0 else "arrow-left"
            else:
                arrow_symbol = "arrow-up" if dy > 0 else "arrow-down"

            fig.add_trace(go.Scattergeo(
                lat=[pais.lat, destino.lat],
                lon=[pais.lon, destino.lon],
                mode="lines",
                line=dict(color="blue", width=2),
                showlegend=False,
                hoverinfo="skip"
            ))

            fig.add_trace(go.Scattergeo(
                lat=[destino.lat],
                lon=[destino.lon],
                mode="markers",
                marker=dict(size=12, symbol=arrow_symbol, color="blue"),
                showlegend=False,
                hoverinfo="skip"
            ))

    # BIDIRECTIONAL (Both immigration and emigration - Purple lines)
    for iso2 in bidirectional_isos:
        if iso2 in paises:
            other = paises[iso2]
            
            fig.add_trace(go.Scattergeo(
                lat=[other.lat, pais.lat],
                lon=[other.lon, pais.lon],
                mode="lines",
                line=dict(color="purple", width=3),
                showlegend=False,
                hoverinfo="skip"
            ))

    return fig


# actualización dinámica

app = dash.Dash(__name__)
server = app.server
app.title = "Mapa movilidad UE"

app.layout = html.Div([
    # Selector de idioma
    html.Div([
        html.Label("Language / Idioma:", style={"marginRight": "10px"}),
        dcc.RadioItems(
            id="language-selector",
            options=[
                {"label": " Español", "value": "es"},
                {"label": " English", "value": "en"}
            ],
            value="es",
            inline=True,
            style={"display": "inline-flex", "gap": "20px"}
        )
    ], style={
        "position": "absolute",
        "top": "10px",
        "left": "10px",
        "background": "white",
        "padding": "10px",
        "borderRadius": "5px",
        "zIndex": "999"
    }),
    
    # Legend and data source
    html.Div([
        html.H4("Legend", style={"marginTop": "0", "marginBottom": "15px"}),
        
        # Orange line - Immigration
        html.Div([
            html.Div(style={
                "display": "inline-block",
                "width": "30px",
                "height": "3px",
                "backgroundColor": "orange",
                "marginRight": "10px",
                "verticalAlign": "middle"
            }),
            html.Span("Immigration", style={"verticalAlign": "middle"})
        ], style={"marginBottom": "12px"}),
        
        # Blue line - Emigration
        html.Div([
            html.Div(style={
                "display": "inline-block",
                "width": "30px",
                "height": "3px",
                "backgroundColor": "blue",
                "marginRight": "10px",
                "verticalAlign": "middle"
            }),
            html.Span("Emigration", style={"verticalAlign": "middle"})
        ], style={"marginBottom": "12px"}),
        
        # Purple line - Bidirectional
        html.Div([
            html.Div(style={
                "display": "inline-block",
                "width": "30px",
                "height": "3px",
                "backgroundColor": "purple",
                "marginRight": "10px",
                "verticalAlign": "middle"
            }),
            html.Span("Bidirectional Flow", style={"verticalAlign": "middle"})
        ], style={"marginBottom": "20px"}),
        
        # Data source
        html.Div([
            html.P(
                [
                    "Data obtained from ",
                    html.A("https://data.europa.eu", 
                           href="https://data.europa.eu", 
                           target="_blank",
                           style={"color": "#0066cc", "textDecoration": "underline"})
                ],
                style={"fontSize": "12px", "margin": "0", "color": "#666"}
            )
        ], style={"borderTop": "1px solid #ddd", "paddingTop": "10px"})
        
    ], style={
        "position": "absolute",
        "left": "10px",
        "top": "80px",
        "background": "white",
        "padding": "15px",
        "borderRadius": "5px",
        "zIndex": "999",
        "width": "200px",
        "fontSize": "13px"
    }),
    
    dcc.Graph(id="map", figure=mapa_base("es"),
              style={"height":"100vh"}),
    html.Div(id="info",
             style={"position":"absolute",
                    "right":"20px",
                    "top":"20px",
                    "background":"white",
                    "padding":"15px"})
])


@app.callback(
    Output("map","figure"),
    Output("info","children"),
    Input("map","clickData"),
    Input("language-selector", "value"),
    prevent_initial_call=False
)
def update(click, lang):

    fig = mapa_base(lang)

    if not click:
        return fig, t("click_country", lang)

    iso = click["points"][0]["customdata"]
    pais = paises[iso]

    fig = agregar_flechas(fig, pais, lang)

    # mensaje si no hay datos
    def render_section(title, total, relaciones, lang):
        if total == 0 or not relaciones:
            return [
                html.H4(title),
                html.P(t("no_data", lang))
            ]
        else:
            return [
                html.H4(title),
                html.P(f"{t('total', lang)}: {total}"),
                html.Ul([
                    # FIXED: Translate country names using t() function
                    html.Li(f"{t(f'countries.{r.iso2}', lang)}: {r.valor}")
                    for r in relaciones
                ])
            ]

    # Obtener nombre del país en el idioma seleccionado
    country_name = t(f"countries.{iso}", lang)

    info = html.Div([
        html.H3(country_name),
        *render_section(t("reception", lang), pais.recepcion.total, pais.recepcion.relaciones, lang),
        *render_section(t("emission", lang), pais.emision.total, pais.emision.relaciones, lang)
    ])

    return fig, info


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))
