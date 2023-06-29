import os
import dash
from dash import html
import dash_bootstrap_components as dbc
from flask import Flask, request, render_template
from saagieapi import SaagieApi
from datetime import datetime
import flask

# conf
text_color = '#263D5C'
text_color2 = '#587193'
btn_color = "primary"
border_color = "#D9DBE3"
border_radius = 6
btn_style = {"height": 40, "width": 100, "border-radius": border_radius}

server = flask.Flask(__name__)
app = dash.Dash(__name__,
                server=server,
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                routes_pathname_prefix='/dash/',
                url_base_pathname=os.environ["SAAGIE_BASE_PATH"] + "/")

project_name = os.getenv("SAAGIE_PROJECT_NAME")
pipeline_name = os.getenv("SAAGIE_PIPELINE_NAME")
payload_history = []

saagie_client = SaagieApi(url_saagie=os.environ["SAAGIE_URL"],
                          id_platform=os.environ["SAAGIE_PLATFORM_ID"],
                          user=os.environ["SAAGIE_LOGIN"],
                          password=os.environ["SAAGIE_PWD"],
                          realm=os.environ["SAAGIE_REALM"])


@server.route('/', methods=['GET', 'POST'])
def receive_webhook():
    if request.method == 'POST':
        payload = request.get_json()
        esri_dict = payload["feature"]
        feature_attributes = esri_dict["attributes"]
        feature_geometry = esri_dict["geometry"]
        print("Attributes")
        print("a quel heure vous l'avez vu:",
              datetime.fromtimestamp(feature_attributes["a_quel_heure_vous_lavez_vu"] / 1000))
        print("quel tete:", feature_attributes["quel_tete"])
        print("Genance:", feature_attributes["g_ne_g_n_rer"])
        print("utilite de ce survey:", feature_attributes["utilit_de_ce_survey"])
        print("global id:", feature_attributes["globalid"])
        print("object id:", feature_attributes["objectid"])
        print("Geometry")
        print("geometryType:", feature_geometry["geometryType"])
        print("geometry x:", feature_geometry["x"])
        print("geometry y:", feature_geometry["y"])
        print("geometry spatialReference:", feature_geometry["spatialReference"])
        payload['current_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload_history.append(esri_dict)  # Add the payload to the history list
        saagie_client.pipelines.run_with_callback(pipeline_id=pipeline_id)
        return 'Webhook received successfully'
    else:
        return payload_history
        # return render_template('./assets/index.html', payload_history=payload_history)


app.layout = dbc.Container(fluid=True, children=[
    dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src="assets/saipem_logo.png", height="50px")),
                            dbc.Col(dbc.NavbarBrand("Saipem - ESRI payloads APP", className="ms-3",
                                                    style={"color": text_color})),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="https://www.saipem.fr/",
                    style={"textDecoration": "none", "margin-left": "0px"},
                ),
                dbc.Button("⟳ Refresh", id="refresh", n_clicks=0, size='mb', href='/',
                           color="dark",
                           outline=True,
                           style={"height": "1%", "font-size": 14, "width": "10",
                                  "border-radius": border_radius})

            ],
        ),
        color="#b8c9e1",
        className="mb-1",
        expand=True
    ),
    dbc.Row(html.Br(), class_name=".mb-4"),

    # Main part
    dbc.Row("Recent payloads:"),
    dbc.Row(
        className="payload",
        children=[

            html.Ul(id='my-list', children=[
                html.Li(children=[
                    dbc.Card([
                        dbc.CardHeader(f"Object ID: {i['attributes']['objectid']}"),
                        dbc.CardBody([
                            dbc.Row(
                                f"A quel heure vous l'avez vu: {datetime.fromtimestamp(i['attributes']['a_quel_heure_vous_lavez_vu'] / 1000)}"),
                            dbc.Row(f"Quel tete: {i['attributes']['quel_tete']}"),
                            dbc.Row(f"Genance: {i['attributes']['g_ne_g_n_rer']}"),
                            dbc.Row(f"Utilite de ce survey: {i['attributes']['utilit_de_ce_survey']}"),
                            dbc.Row(f"Geometry: {i['geometry']}"),

                        ]),
                    ],
                    ),
                ]
                ) for i in payload_history])
        ],
    ),

])

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
