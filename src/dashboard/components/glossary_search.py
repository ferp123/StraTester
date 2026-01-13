import dash_bootstrap_components as dbc
from dash import html, dcc

def glossary_search_component():
    return html.Div(
        [
            dbc.InputGroup([
                dbc.Input(id='glossary-search-input', placeholder='Search trading term...', type='text', debounce=True),
                dbc.Button('Search', id='glossary-search-btn', color='primary', n_clicks=0),
            ], className='mb-2', style={'maxWidth': 320, 'float': 'right'}),
            html.Div(id='glossary-search-result', style={'position': 'absolute', 'right': 0, 'top': 50, 'zIndex': 10, 'maxWidth': 400})
        ],
        style={'position': 'relative', 'display': 'inline-block', 'verticalAlign': 'top'}
    )
