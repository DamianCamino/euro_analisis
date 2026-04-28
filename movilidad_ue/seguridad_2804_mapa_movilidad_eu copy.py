import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go

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


# relación de coordenadas para el mapa
coords = {
"AT": ("Austria",47.51,14.55),
"BE": ("Bélgica",50.85,4.35),
"BG": ("Bulgaria",42.69,23.32),
"CY": ("Chipre",35.12,33.43),
"CZ": ("República Checa",50.07,14.43),
"CZ_SK": ("República Checa",50.07,14.43),  
"DE": ("Alemania",51.16,10.45),
"DK": ("Dinamarca",55.67,12.56),
"EE": ("Estonia",59.43,24.75),
"EL": ("Grecia",37.98,23.72),
"ES": ("España",40.46,-3.74),
"FI": ("Finlandia",60.17,24.93),
"FR": ("Francia",48.85,2.35),
"HR": ("Croacia",45.1,15.2),
"HU": ("Hungría",47.16,19.50),
"IE": ("Irlanda",53.34,-6.26),
"IT": ("Italia",41.87,12.56),
"LT": ("Lituania",54.68,25.27),
"LU": ("Luxemburgo",49.61,6.13),
"LV": ("Letonia",56.94,24.10),
"MT": ("Malta",35.89,14.51),
"NL": ("Países Bajos",52.13,5.29),
"PL": ("Polonia",52.23,21.01),
"PT": ("Portugal",38.72,-9.13),
"RO": ("Rumania",45.94,24.96),
"SE": ("Suecia",59.32,18.06),
"SI": ("Eslovenia",46.05,14.50),
"SK": ("Eslovaquia",48.14,17.10),
}


# los datos han sido sacados de migr_imm1ctz, del portal de datos de Eurostat
# para facilidad de uso, los divido en recepción, según los valores citizen y geo del repositorio original
#

df_recep = pd.read_csv("recepcion_nuevo.csv")
df_emi = pd.read_csv("emigracion_nuevo.csv")




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

print(f"Total países creados: {len(paises)}")
for iso, p in paises.items():
    if p.recepcion.relaciones or p.emision.relaciones:
        print(f"{iso}: {len(p.recepcion.relaciones)} rec, {len(p.emision.relaciones)} emi")


def mapa_base():

    lats,lons,texts,isos=[],[],[],[]

    for iso,p in paises.items():
        lats.append(p.lat)
        lons.append(p.lon)
        #texts.append(p.nombre)
        isos.append(iso)

    fig = go.Figure(go.Scattergeo(
        lat=lats,
        lon=lons,
        text=texts,
        customdata=isos,
        mode="markers+text",
        textposition="top center",
        marker=dict(size=8,color="grey")
    ))

    fig.update_geos(scope="europe", showcountries=True)

    return fig


def agregar_flechas(fig, pais):

    # RECEPCION 
    for r in pais.recepcion.relaciones:
        if r.iso2 in paises:
            origen = paises[r.iso2]

            fig.add_trace(go.Scattergeo(
                lat=[origen.lat, pais.lat],
                lon=[origen.lon, pais.lon],
                mode="lines",
                line=dict(color="blue",width=2),
                showlegend=False
            ))

    # EMISION 
    for r in pais.emision.relaciones:
        if r.iso2 in paises:
            destino = paises[r.iso2]
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
                line=dict(color="orange", width=2),
                showlegend=False
            ))

            fig.add_trace(go.Scattergeo(
                lat=[destino.lat],
                lon=[destino.lon],
                mode="markers",
                marker=dict(size=12, symbol=arrow_symbol, color="orange"),
                showlegend=False
            ))

    return fig


# actualización dinámica

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id="map", figure=mapa_base(),
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
    Input("map","clickData")
)
def update(click):

    fig = mapa_base()

    if not click:
        return fig,"Click en un país"

    iso = click["points"][0]["customdata"]
    pais = paises[iso]

    fig = agregar_flechas(fig,pais)

    info = html.Div([
        html.H3(pais.nombre),

        html.H4("Recepción"),
        html.P(f"Total: {pais.recepcion.total}"),
        html.Ul([
            html.Li(f"{r.nombre}: {r.valor}")
            for r in pais.recepcion.relaciones
        ]),

        html.H4("Emisión"),
        html.P(f"Total: {pais.emision.total}"),
        html.Ul([
            html.Li(f"{r.nombre}: {r.valor}")
            for r in pais.emision.relaciones
        ])
    ])

    return fig, info


if __name__ == "__main__":
    app.run(debug=True)

    