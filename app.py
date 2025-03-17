import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import json
import os
from concurrencia import ejecutar_concurrencia
from flask import Flask, send_from_directory

# Inicializar Flask como backend
server = Flask(__name__, template_folder='templates')
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.LUX])

# Ruta de la carpeta donde están las evidencias
EVIDENCIAS_DIR = os.path.abspath("data/evidencias")

# Servir imágenes estáticamente desde el servidor Flask
@server.route("/evidencias/<path:filename>")
def serve_image(filename):
    return send_from_directory(EVIDENCIAS_DIR, filename)

# Layout de la aplicación
app.layout = html.Div([
    # Navbar
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Inicio", href="#")),
            dbc.NavItem(dbc.NavLink("Acerca de", href="#")),
        ],
        brand="Sistema de Concurrencia - Team QA",
        brand_href="#",
        color="primary",
        dark=True,
        fluid=True,
    ),

    # Contenido principal
    dbc.Container([
        html.H1("Sistema de Concurrencia - Team QA", className="text-center mt-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Label("Cantidad de conexiones:"),
                        dcc.Input(id="num_conexiones", type="number", value=5, min=1, step=1, className="form-control"),
                        html.Br(),
                        dbc.Label("Modo de ejecución:"),
                        dcc.RadioItems(
                            id="modo_ejecucion",
                            options=[
                                {"label": "Headless", "value": "headless"},
                                {"label": "Visible", "value": "visible"}
                            ],
                            value="headless",
                            inline=True
                        ),
                        html.Br(),
                        dbc.Button("Ejecutar", id="btn_ejecutar", color="primary", className="mt-2"),
                        html.Br(),
                        html.Div(id="mensaje", className="mt-3")
                    ])
                ], className="mb-4")
            ], width=6),
        ], className="mt-4"),

        html.Hr(),
        html.H3("Resultados", className="mt-4"),
        dcc.Loading(
            id="loading",
            type="circle",
            children=[html.Div(id="tabla_resultados")]  # Asegúrate de que esté aquí
        ),

        # Modal para ver imagen en grande
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Evidencia")),
                dbc.ModalBody(html.Img(id="imagen_modal", src="", style={"width": "100%"})),
                dbc.ModalFooter(
                    dbc.Button("Cerrar", id="cerrar_modal", className="ml-auto", color="secondary")
                ),
            ],
            id="modal",
            is_open=False,
            centered=True,
            size="lg",
        )
    ], fluid=True),

    # Footer
    dbc.Container([
        html.Footer([
            html.P("© 2023 Team QA. Todos los derechos reservados.", className="text-center"),
        ])
    ], fluid=True, className="mt-4")
])

# Callback para ejecutar la concurrencia y mostrar resultados
@app.callback(
    Output("tabla_resultados", "children"),
    Output("mensaje", "children"),
    Input("btn_ejecutar", "n_clicks"),
    State("num_conexiones", "value"),
    State("modo_ejecucion", "value"),
    prevent_initial_call=True
)
def ejecutar(n_clicks, num_conexiones, modo_ejecucion):
    mensaje = "Ejecutando consultas..."
    ejecutar_concurrencia(num_conexiones, modo_ejecucion)

    ruta_json = "data/resultados.json"
    if not os.path.exists(ruta_json):
        return "", "No se encontraron resultados."

    with open(ruta_json, "r", encoding="utf-8") as f:
        try:
            resultados = json.load(f)
        except json.JSONDecodeError:
            return "", "Error al leer el archivo de resultados."

    if not resultados:
        return "", "No hay datos disponibles en el archivo de resultados."

    # Construcción de la tabla con imágenes
    columns = [
        {"name": "Usuario ID", "id": "usuario_id"},
        {"name": "RUT", "id": "rut"},
        {"name": "Estado", "id": "status"},
        {"name": "Evidencia", "id": "evidencia", "presentation": "markdown"},
    ]

    for resultado in resultados:
        if "evidencia" in resultado:
            resultado["evidencia"] = f'<a href="#" id="imagen_{resultado["usuario_id"]}"><img src="/evidencias/{os.path.basename(resultado["evidencia"])}" width="100"/></a>'
        else:
            resultado["evidencia"] = "No disponible"

    table = dash_table.DataTable(
        columns=columns,
        data=resultados,
        page_size=10,
        sort_action="native",
        filter_action="native",
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        markdown_options={"html": True}
    )

    return table, "Proceso completado."

# Callback combinado para abrir y cerrar el modal con la imagen seleccionada
@app.callback(
    Output("modal", "is_open"),
    Output("imagen_modal", "src"),
    Input("cerrar_modal", "n_clicks"),
    Input({"type": "imagen_click", "index": dash.ALL}, "n_clicks"),
    State("modal", "is_open"),
    prevent_initial_call=True
)
def manejar_modal(cerrar_click, imagen_clicks, modal_abierto):
    ctx = dash.callback_context
    if not ctx.triggered:
        return modal_abierto, ""

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Si se hizo clic en el botón "Cerrar", se cierra el modal
    if triggered_id == "cerrar_modal":
        return False, ""

    # Si se hizo clic en una imagen, se obtiene la ruta y se abre el modal
    imagen_id = triggered_id.split("_")[1]
    ruta_json = "data/resultados.json"

    with open(ruta_json, "r", encoding="utf-8") as f:
        resultados = json.load(f)

    for resultado in resultados:
        if str(resultado["usuario_id"]) == imagen_id and "evidencia" in resultado:
            imagen_src = f"/evidencias/{os.path.basename(resultado['evidencia'])}"
            return True, imagen_src

    return modal_abierto, ""

# Ejecutar el servidor
if __name__ == "__main__":
    app.run_server(debug=True, port=8900)
