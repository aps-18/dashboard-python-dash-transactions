import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import calendar
from dash import Dash, dcc, html, Input, Output, dash_table, callback
import dash_bootstrap_components as dbc

# 1. Charger `data.csv` dans un DataFrame `df`.
df = pd.read_csv("data/data.csv")

# 2. Garder uniquement les colonnes utiles ('CustomerID', 'Gender', 'Location', 'Product_Category', 'Quantity', 'Avg_Price', 'Transaction_Date', 'Month', 'Discount_pct').
df = df[['CustomerID', 'Gender', 'Location', 'Product_Category', 'Quantity',
         'Avg_Price', 'Transaction_Date', 'Month', 'Discount_pct']].copy()

# 3. Remplacer les valeurs manquantes dans `CustomerID` par 0 et convertir `CustomerID` en entier.
df['CustomerID'] = df['CustomerID'].fillna(0).astype(int)

# 4. Convertir `Transaction_Date` en date.
df['Transaction_Date'] = pd.to_datetime(df['Transaction_Date'])

# 5. Créer `Total_price` avec la remise.
df['Total_price'] = df['Quantity'] * df['Avg_Price'] * (1 - df['Discount_pct'] / 100)

# 6. Nettoyer Location
df['Location'] = df['Location'].fillna("Inconnue").astype(str)

# 1. `calculer_chiffre_affaire(data)`
def calculer_chiffre_affaire(data):
    return data["Total_price"].sum()

# 2. `frequence_meilleure_vente(data, top=10, ascending=False)`
def frequence_meilleure_vente(data, top=10, ascending=False):
    freq = (
        data.groupby(["Product_Category", "Gender"])
        .size()
        .reset_index(name="Nb_ventes")
    )

    top_categories = (
        freq.groupby("Product_Category")["Nb_ventes"]
        .sum()
        .sort_values(ascending=ascending)
        .head(top)
        .index
    )

    freq_top = freq[freq["Product_Category"].isin(top_categories)].copy()

    ordre = (
        freq_top.groupby("Product_Category")["Nb_ventes"]
        .sum()
        .sort_values(ascending=ascending)
        .index
        .tolist()
    )

    return freq_top, ordre


# 3. `indicateur_du_mois(data, current_month=12, freq=True, abbr=False)`
def indicateur_du_mois(data, current_month=12, freq=True, abbr=False):
    data_month = data[data["Month"] == current_month]
    mois_precedent = 12 if current_month == 1 else current_month - 1
    data_prev = data[data["Month"] == mois_precedent]

    if freq:
        valeur = len(data_month)
        reference = len(data_prev)
    else:
        valeur = data_month["Total_price"].sum()
        reference = data_prev["Total_price"].sum()

    mois = calendar.month_abbr[current_month] if abbr else calendar.month_name[current_month]

    return {
        "mois": mois,
        "valeur": valeur,
        "reference": reference,
        "delta": valeur - reference
    }

# 1. `barplot_top_10_ventes(data)`
def barplot_top_10_ventes(data):
    freq_top, ordre = frequence_meilleure_vente(data, top=10, ascending=False)

    fig = px.bar(
        freq_top,
        x="Nb_ventes",
        y="Product_Category",
        color="Gender",
        orientation="h",
        title="Fréquence des 10 meilleures ventes(nb de ventes)"
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Nombre de ventes",
        yaxis_title="Categorie de produit",
        legend_title="Sexe",
        barmode="group",
        height=380,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    fig.update_yaxes(
        categoryorder="array",
        categoryarray=ordre,
        autorange="reversed"
    )

    return fig


# 2. `plot_evolution_chiffre_affaire(data)`
def plot_evolution_chiffre_affaire(data):
    evolution = (
        data.resample("W", on="Transaction_Date")["Total_price"]
        .sum()
        .reset_index(name="Chiffre_Affaire")
    )

    fig = px.line(
        evolution,
        x="Transaction_Date",
        y="Chiffre_Affaire",
        title="Évolution du chiffre d'affaire par semaine"
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Semaine",
        yaxis_title="Chiffre d'affaire",
        height=350,
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return fig


# 3. `plot_chiffre_affaire_mois(data)`
def plot_chiffre_affaire_mois(data, current_month=12):
    indic = indicateur_du_mois(data, current_month=current_month, freq=False)

    fig = go.Figure(go.Indicator(
        mode="number+delta",
        value=indic["valeur"],
        number={"valueformat": ".3s"},
        delta={"reference": indic["reference"], "relative": False},
        title={"text": indic["mois"]}
    ))

    fig.update_layout(
        template="plotly_white",
        height=180,
        margin=dict(l=10, r=10, t=20, b=0)
    )

    return fig


# 4. `plot_vente_mois(data, abbr=False)`
def plot_vente_mois(data, current_month=12):
    indic = indicateur_du_mois(data, current_month=current_month, freq=True)

    fig = go.Figure(go.Indicator(
        mode="number+delta",
        value=indic["valeur"],
        number={"valueformat": ".0f"},
        delta={"reference": indic["reference"], "relative": False},
        title={"text": indic["mois"]}
    ))

    fig.update_layout(
        template="plotly_white",
        height=180,
        margin=dict(l=10, r=10, t=20, b=0)
    )

    return fig


# table pour le dashboard
def table_100_dernieres_ventes(data):
    table = (
        data.sort_values("Transaction_Date", ascending=False)
        .head(100)
        .copy()
    )

    table = table[[
        "Transaction_Date", "Gender", "Location", "Product_Category",
        "Quantity", "Avg_Price", "Discount_pct"
    ]]

    table["Transaction_Date"] = table["Transaction_Date"].dt.strftime("%Y-%m-%d")
    table["Avg_Price"] = table["Avg_Price"].round(2)

    table = table.rename(columns={
        "Transaction_Date": "Date",
        "Product_Category": "Product Category",
        "Avg_Price": "Avg Price",
        "Discount_pct": "Discount Pct"
    })

    return table


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


if __name__ == "__main__":
    app.run()
