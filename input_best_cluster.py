import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd

# Initialize the Dash app
app = dash.Dash(__name__)

# Read data from the Excel file
try:
    df = pd.read_excel('dash_visu_export.xlsx', sheet_name='Sheet1')
    if not all(column in df.columns for column in ['UTCI', 'GWP', 'LCC', 'cluster']):
        raise ValueError("Some essential columns are missing from the Excel sheet.")
except Exception as e:
    print(f"Error reading the Excel file: {e}")
    df = pd.DataFrame()

parameters = [
    "Baumanteil [%]", "PV-Dach [%]", "PV battery capacity", "PV-facade-% south",
    "Fensterflächenanteil", "Fenster g-Wert", "Gründachstärke",
    "Kronendurchmesser", "Baumhöhe", "Kronentransparenz Sommer",
    "Kronentransparenz Winter", "Albedo Fassade", "Straßenbreite", "PV Ost-West Fassade [%]"
]

app.layout = html.Div([
    *[html.Div([
        html.Label(param),
        dcc.Input(id=f'input-{param}', type='number', value=df[param].mean() if not df.empty else 0)
    ]) for param in parameters],
    html.Button('Find Best Cluster', id='submit-button'),
    html.Div(id='best-cluster-output')
])


@app.callback(
    Output('best-cluster-output', 'children'),
    [Input(f'input-{param}', 'value') for param in parameters]
)
def find_best_cluster(*args):
    if df.empty:
        return "Error loading data."

    input_values = {param: value for param, value in zip(parameters, args)}

    # Compute distance of each row from the input values and find the row with the smallest distance
    differences = df[parameters].apply(lambda row: sum((row - pd.Series(input_values)) ** 2), axis=1)
    best_cluster = df.loc[differences.idxmin(), 'cluster']

    return f'The most suitable cluster for the given parameters is: Cluster {best_cluster}'


if __name__ == '__main__':
    app.run_server(debug=True)
