import chart_studio
import chart_studio.plotly as py

from mapa_movilidad_eu import mapa_base

# Configura tus credenciales de Plotly Cloud aquí.
# Alternativamente, puedes usar las variables de entorno PLOTLY_USERNAME y PLOTLY_API_KEY.
USERNAME = "TU_USUARIO"
API_KEY = "TU_API_KEY"

chart_studio.tools.set_credentials_file(username=USERNAME, api_key=API_KEY)


def upload_mapa():
    fig = mapa_base()
    url = py.plot(fig, filename="mapa_movilidad_eu", auto_open=False, sharing="public")
    print("Gráfico subido a Plotly Cloud:", url)
    return url


if __name__ == "__main__":
    upload_mapa()
