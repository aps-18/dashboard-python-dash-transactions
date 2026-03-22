# dashboard final Dash
from dash import Dash, dcc, html, dash_table, Input, Output

app = Dash(__name__)
server = app.server

zones = sorted(df["Location"].unique())

app.layout = html.Div([

    html.Div([
        html.H1(
            "ECAP STORE",
            style={"color": "white", "margin": "0", "fontSize": "28px"}
        ),

        dcc.Dropdown(
            id="zone-filter",
            options=[{"label": z, "value": z} for z in zones],
            placeholder="Choisissez des zones",
            multi=False,
            style={"width": "300px", "backgroundColor": "white"}
        )
    ], style={
        "backgroundColor": "#2A6FBB",
        "padding": "10px 20px",
        "display": "flex",
        "justifyContent": "space-between",
        "alignItems": "center",
        "marginBottom": "20px"
    }),

    html.Div([
        html.Div([dcc.Graph(id="ca_mois", config={"displayModeBar": False})],
                 style={"width": "18%"}),

        html.Div([dcc.Graph(id="vente_mois", config={"displayModeBar": False})],
                 style={"width": "18%"}),

        html.Div([dcc.Graph(id="evolution_ca", config={"displayModeBar": False})],
                 style={"width": "60%"})
    ], style={
        "display": "flex",
        "justifyContent": "space-between",
        "alignItems": "flex-start",
        "marginBottom": "20px"
    }),

    html.Div([
        html.Div([dcc.Graph(id="top_ventes", config={"displayModeBar": False})],
                 style={"width": "33%"}),

        html.Div([
            html.H4("Table des 100 dernières ventes", style={"marginTop": "0px"}),
            dash_table.DataTable(
                id="table_ventes",
                page_size=10,
                style_table={"overflowX": "auto"},
                style_cell={
                    "textAlign": "left",
                    "padding": "8px",
                    "fontFamily": "Arial",
                    "fontSize": "13px"
                },
                style_header={
                    "backgroundColor": "#f2f2f2",
                    "fontWeight": "bold"
                }
            )
        ], style={"width": "65%"})
    ], style={
        "display": "flex",
        "justifyContent": "space-between",
        "alignItems": "flex-start"
    })

], style={"margin": "20px"})


@app.callback(
    Output("ca_mois", "figure"),
    Output("vente_mois", "figure"),
    Output("evolution_ca", "figure"),
    Output("top_ventes", "figure"),
    Output("table_ventes", "data"),
    Output("table_ventes", "columns"),
    Input("zone-filter", "value")
)
def update_dashboard(zone_selection):

    if zone_selection is None:
        dff = df.copy()
    else:
        dff = df[df["Location"] == zone_selection].copy()

    fig1 = plot_chiffre_affaire_mois(dff)
    fig2 = plot_vente_mois(dff)
    fig3 = plot_evolution_chiffre_affaire(dff)
    fig4 = barplot_top_10_ventes(dff)

    table = table_100_dernieres_ventes(dff)

    return (
        fig1,
        fig2,
        fig3,
        fig4,
        table.to_dict("records"),
        [{"name": col, "id": col} for col in table.columns]
    )


print("Dashboard disponible ici : http://127.0.0.1:8050/")
app.run()