# Entry point for Dash app


import dash
import dash_bootstrap_components as dbc
from dash import Output, Input, State
from dashboard.layout import layout
from dashboard.callbacks import register_callbacks
from dashboard.glossary_callbacks import register_glossary_callbacks


# Use a modern Bootstrap theme (e.g., FLATLY)
BOOTSTRAP_THEME = dbc.themes.FLATLY

# Create Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[BOOTSTRAP_THEME])


# Set layout
app.layout = layout


register_callbacks(app)
register_glossary_callbacks(app)



if __name__ == '__main__':
    app.run_server(debug=True)
# Entry point for Dash app
# Will import layout, callbacks, etc.
