import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash.dependencies as dps
import plotly.graph_objs as go
import pandas as pd
import json
import numpy as np

df_test = pd.DataFrame({'A': [5], 'B': [6], 'C': [7]})

df = pd.read_csv(
    'https://gist.githubusercontent.com/chriddyp/'
    'cb5392c35661370d95f300086accea51/raw/'
    '8e0768211f6b747c0db42a9ce9a0937dafcbd8b2/'
    'indicators.csv')

external_stylesheet = [
    {
        'href': '/assets/styles/main.css',
        'rel': 'stylesheet',
        'crossorigin': 'anonymous'
    },
    {
        'href': '/assets/styles/loading.css',
        'rel': 'stylesheet',
        'crossorigin': 'anonymous'
    },
    {
        'href': '/assets/styles/dark_style_datatable.css',
        'rel': 'stylesheet',
        'crossorigin': 'anonymous'
    }
]

app = dash.Dash(__name__, external_stylesheet=external_stylesheet)


def table_data_from_dataframe(dataframe):
    return [{"name": c, "id": c} for c in dataframe.columns], dataframe.to_dict('records')


def get_nth_alphabet_letter(n):
    assert 0 <= n <= 25
    return chr(n + 65)


def number_to_excel_column_name(num):
    assert num >= 0

    construction_list = []
    while num > 25:
        if len(construction_list) == 0 or construction_list[-1] == 25:
            construction_list.append(0)
        else:
            construction_list[-1] += 1
        num -= 25

    construction_list = reversed([num] + construction_list)

    return ''.join(get_nth_alphabet_letter(n) for n in construction_list)


tst_data = table_data_from_dataframe(df_test)

app.layout = html.Div(children=[
    html.Div([
        dash_table.DataTable(
            id='test-table',
            columns=tst_data[0],
            data=tst_data[1],
            style_cell={
                'minWidth': '40px', 'maxWidth': '180px',
                'whiteSpace': 'no-wrap',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis'
            },
            style_table={
                'overflowX': 'scroll'
            },
            editable=True

        )
    ], style={'display': 'inline-block', 'float': 'left'}),

    html.Div([
        html.Button('+', id='add-column-button')
    ], style={'display': 'inline-block'}),

    html.Div([
        html.Button('+', id='add-row-button')
    ], style={'display': 'block'}, className='twelve columns'),

    html.Div(id='info-box', style={'display': 'none'}),

    html.Div([
        dcc.Input(
            placeholder='Enter an expression...',
            type='text',
            value='',
            id='expression-textfield'
        ),
        html.Button('Submit', id='expression-submit-button', style={'display': 'inline-block', 'position': 'relative'}),
        html.Div([
            'Invalid expression'
        ], id='error-tooltip', style={'display': 'none'}, className='tooltip')
    ], style={'display': 'inline-block'}, className='twelve columns'),

    html.Div(id='error-signal', style={'display': 'none'})
])


@app.callback(
    [dps.Output('error-tooltip', 'className'),
     dps.Output('error-tooltip', 'style'),
     dps.Output('error-tooltip', 'children')],
    [dps.Input('error-signal', 'children')]
)
def error_handling(signal):
    if signal == 'True':
        return 'tooltip active', {'display': 'inline-block'}, "Invalid expression"
    else:
        return 'tooltipe out', {'display': 'inline-block'}, ""


@app.callback(
    [dps.Output('test-table', 'columns'),
     dps.Output('test-table', 'data'),
     dps.Output('error-signal', 'children')],
    [dps.Input('add-row-button', 'n_clicks_timestamp'),
     dps.Input('add-column-button', 'n_clicks_timestamp'),
     dps.Input('expression-submit-button', 'n_clicks_timestamp')],
    [dps.State('expression-textfield', 'value')]
)
def modify_table_button(row_timestamp, column_timestamp, submit_timestamp, expression_value):
    global df_test

    error_signal = "False"
    sorted_button_click = sorted(
        [(idx, v) for idx, v in enumerate([row_timestamp, column_timestamp, submit_timestamp]) if v is not None],
        reverse=True, key=lambda x: x[1])
    if len(sorted_button_click) > 0:
        last_clicked_button = sorted_button_click[0][0]

        if last_clicked_button == 0:
            df_test = df_test.append(pd.DataFrame({c: [' '] for c in df_test.columns}))
        elif last_clicked_button == 1:
            df_test[number_to_excel_column_name(len(df_test.columns))] = [' ' for _ in range(len(df_test.index))]
        elif last_clicked_button == 2:
            assign_split = expression_value.split('=')
            check_assignment = len(assign_split) == 2 and assign_split[0].strip() in df_test.columns
            assigned_column = assign_split[0].strip()
            parsed_expression = [s.strip() for s in assign_split[1].split('+')]
            print(list(col in df_test.columns for col in parsed_expression))
            print(np.all([col in df_test.columns for col in parsed_expression]))
            if check_assignment and np.all([col in df_test.columns for col in parsed_expression]):
                df_test[assigned_column] = sum(pd.to_numeric(df_test[s], errors='coerce').fillna(0) for s in parsed_expression)
            else:
                error_signal = "True"

    res1, res2 = table_data_from_dataframe(df_test)
    return res1, res2, error_signal


@app.callback(
    dps.Output('info-box', 'children'),
    [dps.Input('test-table', 'data')]
)
def update_data(data):
    global df_test
    df_test = pd.DataFrame.from_dict(data)

    return ' '


if __name__ == "__main__":
    print(f'Dash v{dash.__version__}')
    app.run_server(debug=True)
