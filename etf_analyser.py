import base64
import io
import pandas as pd
import plotly.express as px
import dash
from dash import Dash, dcc, html, Input, Output, State, dash_table
from dash.dependencies import ALL
import json

# Initialize Dash app
app = Dash(__name__, suppress_callback_exceptions=True)

# Global variable to store ETF data
uploaded_etf_data = pd.DataFrame()

# App layout with enhanced UI and user instruction
app.layout = html.Div(
    style={
        'fontFamily': "'Arial', sans-serif",
        'margin': '0',
        'padding': '0',
        'backgroundColor': '#f4f4f8',
        'color': '#333'
    },
    children=[
        html.H1(
            "ETF Analyzer",
            style={
                'color': '#3498db',
                'textAlign': 'center',
                'padding': '20px 0',
                'margin': '0',
                'backgroundColor': '#fff',
                'borderBottom': '2px solid #ecf0f1'
            }
        ),
        html.Div(
            className='container',
            style={
                'width': '80%',
                'margin': 'auto',
                'overflow': 'hidden',
                'padding': '20px',
                'backgroundColor': '#fff',
                'boxShadow': '0 0 10px rgba(0, 0, 0, 0.1)',
                'borderRadius': '8px',
                'marginTop': '20px'
            },
            children=[
                # Upload Section with Instruction
                html.Div([
                    html.H3("Upload CSV File", style={'color': '#3498db', 'marginBottom': '10px'}),
                    html.Div(
                        "Upload a CSV file with the following columns: 'ETF' (ETF ticker), 'Stock' (stock ticker), 'Name' (company name),  'Share' (percentage share). Example: 'SMH','AMD','ADVANCED MICRO DEVICES INC','6.69'.",
                        style={
                            'marginBottom': '15px',
                            'padding': '10px',
                            'backgroundColor': '#f1f8ff',
                            'border': '1px solid #d1e0ff',
                            'borderRadius': '4px',
                            'fontSize': '14px'
                        }
                    ),
                    dcc.Upload(
                        id='upload-data',
                        children=html.Button(
                            'Upload',
                            style={
                                'backgroundColor': '#3498db',
                                'color': 'white',
                                'padding': '10px 20px',
                                'border': 'none',
                                'borderRadius': '5px',
                                'cursor': 'pointer',
                                'fontSize': '16px'
                            }
                        ),
                        multiple=False,
                        style={
                            'borderStyle': 'dashed',
                            'borderWidth': '2px',
                            'borderColor': '#bdc3c7',
                            'backgroundColor': '#fff',
                            'textAlign': 'center',
                            'padding': '20px',
                            'borderRadius': '5px'
                        }
                    ),
                    html.Div(
                        id='file-upload-status',
                        style={
                            'marginTop': '15px',
                            'padding': '10px',
                            'border': '1px solid #ecf0f1',
                            'borderRadius': '4px',
                            'backgroundColor': '#f9f9f9'
                        }
                    )
                ], style={'marginBottom': '30px'}),

                # ETF Selection Section
                html.Div([
                    html.H3("Select ETFs", style={'color': '#3498db', 'marginBottom': '10px'}),
                    dcc.Checklist(
                        id="etf-selector",
                        options=[],
                        value=[],
                        inline=False,
                        style={
                            'maxHeight': '200px',
                            'overflowY': 'auto',
                            'padding': '5px'
                        },
                        inputStyle={'marginRight': '5px', 'marginBottom': '5px'}
                    )
                ], style={
                    'border': '1px solid #bdc3c7',
                    'padding': '15px',
                    'borderRadius': '5px',
                    'marginBottom': '30px',
                    'backgroundColor': '#f9f9f9'
                }),

                # Allocation Section
                html.Div([
                    html.H3("Allocate Funds", style={'color': '#3498db', 'marginBottom': '10px'}),
                    html.Div([
                        html.Span("Total Investment: $", style={'marginRight': '5px', 'fontWeight': 'bold'}),
                        dcc.Input(
                            id="money-input",
                            type="number",
                            placeholder="Enter amount",
                            style={
                                'width': '150px',
                                'padding': '8px',
                                'border': '1px solid #bdc3c7',
                                'borderRadius': '4px',
                                'boxSizing': 'border-box'
                            }
                        )
                    ], style={'marginBottom': '15px'}),
                    html.Div(id="etf-allocation-container", style={'marginTop': '10px'})
                ], style={'marginBottom': '30px'}),

                # Results Section
                html.Div([
                    html.H3("Allocation Summary", style={'color': '#3498db', 'marginBottom': '10px'}),
                    html.Div(
                        id="unallocated-cash-display",
                        style={
                            'marginTop': '10px',
                            'padding': '10px',
                            'border': '1px solid #ecf0f1',
                            'borderRadius': '4px',
                            'backgroundColor': '#f9f9f9',
                            'fontWeight': 'bold'
                        }
                    ),
                    html.Div(
                        id="portfolio-output",
                        style={
                            'marginTop': '20px',
                            'padding': '10px',
                            'border': '1px solid #ecf0f1',
                            'borderRadius': '4px',
                            'backgroundColor': '#f9f9f9'
                        }
                    ),
                    dcc.Graph(id="portfolio-graph", style={'marginTop': '20px'})
                ], style={'marginBottom': '30px'}),

                html.Div(id='download-container'),
                dcc.Download(id="download-allocations")
            ]
        )
    ]
)

# Callback: Handle file upload and update ETF options
@app.callback(
    [Output('file-upload-status', 'children'),
     Output('etf-selector', 'options')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def handle_file_upload(contents, filename):
    global uploaded_etf_data
    if contents is None:
        return "No file uploaded yet.", []
    try:
        content_type, content_string = contents.split(',')
        decoded = io.StringIO(io.BytesIO(base64.b64decode(content_string)).read().decode('utf-8'))
        uploaded_etf_data = pd.read_csv(decoded)
        required_cols = {"ETF", "Name", "Stock", "Share"}
        if not required_cols.issubset(uploaded_etf_data.columns):
            return ("Error: CSV must contain 'ETF', 'Name', 'Stock', and 'Share'.", [])
        etf_options = sorted(uploaded_etf_data["ETF"].unique())
        etf_options = [{"label": etf, "value": etf} for etf in etf_options]
        return f"Uploaded file: {filename}", etf_options
    except Exception as e:
        return f"Error processing file: {str(e)}", []

# Callback: Generate allocation inputs
@app.callback(
    Output("etf-allocation-container", "children"),
    [Input("etf-selector", "value"),
     Input("money-input", "value")],
    [State({'type': 'etf-percentage-input', 'index': ALL}, 'value'),
     State({'type': 'etf-percentage-input', 'index': ALL}, 'id')]
)
def generate_allocation_inputs(selected_etfs, total_money, current_pct_values, current_ids):
    if not selected_etfs or total_money is None:
        return []
    sorted_etfs = sorted(selected_etfs)
    current_values = {id['index']: val for id, val in zip(current_ids, current_pct_values) if val is not None}
    
    if not current_values:
        num_etfs = len(sorted_etfs)
        base_pct = 100 / num_etfs
        total_assigned = 0
        for i, etf in enumerate(sorted_etfs):
            if i == num_etfs - 1:
                pct = round(100 - total_assigned, 1)
            else:
                pct = round(base_pct, 1)
                total_assigned += pct
            current_values[etf] = pct
    
    allocated = sum(current_values.get(etf, 0) for etf in sorted_etfs if etf in current_values)
    remaining_allocation = max(0, 100 - allocated)
    new_etfs = [etf for etf in sorted_etfs if etf not in current_values]
    if new_etfs:
        num_new_etfs = len(new_etfs)
        base_new_pct = remaining_allocation / num_new_etfs if remaining_allocation > 0 else 0
        total_new_assigned = 0
        for i, etf in enumerate(new_etfs):
            if i == num_new_etfs - 1:
                pct = round(remaining_allocation - total_new_assigned, 1)
            else:
                pct = round(base_new_pct, 1)
                total_new_assigned += pct
            current_values[etf] = pct
    total = sum(current_values.values())
    if total > 100:
        last_etf = sorted_etfs[-1]
        current_values[last_etf] -= (total - 100)

    children = []
    for etf in sorted_etfs:
        pct_value = current_values.get(etf, 0)
        monetary_value = round((pct_value / 100) * float(total_money), 2) if total_money else 0
        children.append(html.Div([
            html.Label(f"{etf}", style={'fontWeight': 'bold', 'marginRight': '10px', 'width': '100px', 'display': 'inline-block'}),
            html.Div([
                dcc.Input(
                    id={'type': 'etf-percentage-input', 'index': etf},
                    type='number',
                    value=pct_value,
                    min=0,
                    step=0.1,
                    style={
                        'width': '100px',
                        'padding': '8px',
                        'border': '1px solid #bdc3c7',
                        'borderRadius': '4px',
                        'boxSizing': 'border-box'
                    },
                    debounce=True
                ),
                html.Span("%", style={'marginLeft': '5px', 'fontWeight': 'bold'})
            ], style={'display': 'inline-block', 'marginRight': '20px'}),
            html.Div([
                html.Span("$", style={'marginRight': '5px', 'fontWeight': 'bold'}),
                dcc.Input(
                    id={'type': 'etf-monetary-input', 'index': etf},
                    type='number',
                    value=monetary_value,
                    min=0,
                    step=0.01,
                    style={
                        'width': '150px',
                        'padding': '8px',
                        'border': '1px solid #bdc3c7',
                        'borderRadius': '4px',
                        'boxSizing': 'border-box'
                    },
                    debounce=True
                )
            ], style={'display': 'inline-block'})
        ], style={'marginBottom': '15px'}))
    
    children.append(html.Button(
        'Export Allocations',
        id='export-button',
        style={
            'backgroundColor': '#3498db',
            'color': 'white',
            'padding': '10px 20px',
            'border': 'none',
            'borderRadius': '5px',
            'cursor': 'pointer',
            'fontSize': '16px',
            'marginTop': '20px'
        }
    ))
    return children

# Callback: Update unallocated cash display
@app.callback(
    Output("unallocated-cash-display", "children"),
    [Input({'type': 'etf-percentage-input', 'index': ALL}, 'value'),
     Input("money-input", "value")]
)
def update_unallocated_cash(etf_pct_values, total_money):
    if not etf_pct_values or total_money is None:
        return ""
    clean_pct_values = [float(pct) if pct is not None else 0 for pct in etf_pct_values]
    total_allocated = sum(clean_pct_values)
    remaining_pct = 100 - total_allocated
    unallocated_cash = (remaining_pct / 100) * float(total_money)
    if total_allocated > 100:
        return f"Over-allocated: ${unallocated_cash:,.2f} ({remaining_pct:.1f}%)"
    return f"Unallocated Cash: ${unallocated_cash:,.2f} ({remaining_pct:.1f}%)"

# Callback: Synchronize percentage and monetary inputs
@app.callback(
    [Output({'type': 'etf-percentage-input', 'index': ALL}, 'value'),
     Output({'type': 'etf-monetary-input', 'index': ALL}, 'value')],
    [Input({'type': 'etf-percentage-input', 'index': ALL}, 'value'),
     Input({'type': 'etf-monetary-input', 'index': ALL}, 'value')],
    [State("money-input", "value"),
     State({'type': 'etf-percentage-input', 'index': ALL}, 'id')]
)
def sync_percentage_and_monetary_inputs(etf_pct_values, etf_monetary_values, total_money, etf_ids):
    ctx = dash.callback_context
    if not ctx.triggered or total_money is None or not etf_ids:
        return etf_pct_values, etf_monetary_values

    triggered_prop = ctx.triggered[0]['prop_id']
    triggered_value = ctx.triggered[0]['value']

    try:
        prop_dict = json.loads(triggered_prop.split('.value')[0])
        triggered_etf = prop_dict['index']
        triggered_index = next(i for i, id in enumerate(etf_ids) if id['index'] == triggered_etf)
    except (json.JSONDecodeError, StopIteration):
        return etf_pct_values, etf_monetary_values

    pct_values = [float(pct) if pct is not None else 0 for pct in etf_pct_values]
    monetary_values = [float(val) if val is not None else 0 for val in etf_monetary_values]

    if "etf-percentage-input" in triggered_prop:
        new_pct = max(float(triggered_value or 0), 0)
        new_pcts = [new_pct if i == triggered_index else pct for i, pct in enumerate(pct_values)]
        new_monetary = [round((pct / 100) * float(total_money), 2) for pct in new_pcts]
        return new_pcts, new_monetary

    elif "etf-monetary-input" in triggered_prop:
        new_monetary = max(float(triggered_value or 0), 0)
        new_pct = (new_monetary / float(total_money)) * 100 if total_money != 0 else 0
        new_pcts = [new_pct if i == triggered_index else pct for i, pct in enumerate(pct_values)]
        new_monetary_values = [round((pct / 100) * float(total_money), 2) for pct in new_pcts]
        return new_pcts, new_monetary_values

    return etf_pct_values, etf_monetary_values

# Callback: Update portfolio table and graph
@app.callback(
    [Output("portfolio-output", "children"), Output("portfolio-graph", "figure")],
    [Input("etf-selector", "value"),
     Input("money-input", "value"),
     Input({'type': 'etf-percentage-input', 'index': ALL}, 'value')]
)
def update_portfolio(selected_etfs, total_money, etf_pct_values):
    global uploaded_etf_data
    if uploaded_etf_data.empty:
        return "Please upload a valid CSV file first.", {}
    if not selected_etfs or total_money is None:
        return "Select ETFs and enter money to allocate.", {}
    sorted_etfs = sorted(selected_etfs)
    etf_allocations = {etf: (pct if pct is not None else 0)
                       for etf, pct in zip(sorted_etfs, etf_pct_values)}
    etf_monetary = {etf: ((pct / 100) * float(total_money) if pct is not None else 0)
                    for etf, pct in etf_allocations.items()}
    combined_portfolio = {}
    df_selected = uploaded_etf_data[uploaded_etf_data["ETF"].isin(selected_etfs)]
    color_palette = ['#FF9999', '#99CCFF', '#99FF99', '#FFCC99', '#CC99FF', '#FF99CC',
                     '#FF99B3', '#99FFCC', '#99FFFF', '#99B3FF', '#E699FF', '#FF99FF']
    etf_color_mapping = {etf: color_palette[i % len(color_palette)]
                         for i, etf in enumerate(sorted_etfs)}
    for _, row in df_selected.iterrows():
        etf = row["ETF"]
        etf_alloc_pct = etf_allocations.get(etf, 0)
        etf_money = etf_monetary.get(etf, 0)
        stocks = [s.strip() for s in str(row["Stock"]).split(",")]
        percentages = [float(p.strip()) for p in str(row["Share"]).split(",")]
        names = [n.strip() for n in str(row["Name"]).split(",")]
        for stock, stock_pct, name in zip(stocks, percentages, names):
            if stock not in combined_portfolio:
                combined_portfolio[stock] = {"total_pct": 0.0, "monetary_value": 0.0, "etfs": [], "names": []}
            stock_contribution = (stock_pct * etf_alloc_pct) / 100
            combined_portfolio[stock]["total_pct"] += stock_contribution
            combined_portfolio[stock]["monetary_value"] += (stock_pct / 100) * etf_money
            if etf not in combined_portfolio[stock]["etfs"]:
                combined_portfolio[stock]["etfs"].append(etf)
            if name not in combined_portfolio[stock]["names"]:
                combined_portfolio[stock]["names"].append(name)
    portfolio_data = []
    for stock, info in combined_portfolio.items():
        color = etf_color_mapping[info["etfs"][0]] if len(info["etfs"]) == 1 else "#FFFF99"
        portfolio_data.append({
            "Stock": stock,
            "Name": ", ".join(info["names"]),
            "Share": round(info["total_pct"], 2),
            "Monetary Value": round(info["monetary_value"], 2),
            "ETF(s)": ", ".join(info["etfs"]),
            "Color": color
        })
    portfolio_data = sorted(portfolio_data, key=lambda x: x['Share'], reverse=True)
    
    dt = dash_table.DataTable(
        columns=[{"name": col, "id": col} for col in ["Stock", "Name", "Share", "Monetary Value", "ETF(s)"]],
        data=[{k: v for k, v in row.items() if k != "Color"} for row in portfolio_data],
        sort_action="native",
        filter_action="native",
        style_table={
            'border': 'none',
            'borderRadius': '5px',
            'boxShadow': '0 0 5px rgba(0, 0, 0, 0.1)'
        },
        style_header={
            'backgroundColor': '#3498db',
            'color': 'white',
            'fontWeight': 'bold'
        },
        style_cell={
            'padding': '8px',
            'textAlign': 'center'
        },
        style_data_conditional=[
            {
                'if': {'filter_query': "{Stock} = '" + row["Stock"] + "'"},
                'backgroundColor': row["Color"],
                'color': 'black'
            } for row in portfolio_data
        ]
    )
    fig = px.treemap(
        pd.DataFrame(portfolio_data),
        path=["Stock"],
        values="Monetary Value",
        color="Share",
        color_continuous_scale=px.colors.sequential.Viridis,
        title="Portfolio Composition"
    )
    return dt, fig

# Callback: Export ETF allocations
@app.callback(
    Output("download-allocations", "data"),
    Input("export-button", "n_clicks"),
    [State("etf-selector", "value"),
     State("money-input", "value"),
     State({'type': 'etf-percentage-input', 'index': ALL}, 'value'),
     State({'type': 'etf-percentage-input', 'index': ALL}, 'id')]
)
def export_etf_allocations(n_clicks, selected_etfs, total_money, etf_pct_values, etf_ids):
    if not n_clicks or not selected_etfs or total_money is None or not etf_ids:
        return None
    
    etf_pct_map = {id['index']: pct for id, pct in zip(etf_ids, etf_pct_values)}
    sorted_etfs = sorted(selected_etfs)
    allocations_data = []
    for etf in sorted_etfs:
        pct = float(etf_pct_map.get(etf, 0)) if etf_pct_map.get(etf) is not None else 0
        monetary_value = (pct / 100) * float(total_money)
        allocations_data.append({
            'ETF': etf,
            'Share': f"{pct:.2f}%",
            'Monetary_Value': f"${monetary_value:,.2f}"
        })
    
    df_allocations = pd.DataFrame(allocations_data)
    total_pct = sum(float(row['Share'].strip('%')) for row in allocations_data)
    total_money_allocated = sum(float(row['Monetary_Value'].strip('$').replace(',', '')) 
                               for row in allocations_data)
    df_allocations.loc[len(df_allocations)] = ['TOTAL', f"{total_pct:.2f}%", f"${total_money_allocated:,.2f}"]
    return dcc.send_data_frame(df_allocations.to_csv, "etf_allocations.csv", index=False)

if __name__ == "__main__":
    app.run_server(debug=True)