from dash import Input, Output, State, no_update
from dash.exceptions import PreventUpdate
from .components.trading_glossary import TRADING_GLOSSARY
import difflib
from dash import html

def register_glossary_callbacks(app):
    @app.callback(
        Output('glossary-search-result', 'children'),
        [Input('glossary-search-btn', 'n_clicks'), Input('glossary-search-input', 'value')],
        prevent_initial_call=True
    )
    def search_glossary(n_clicks, value):
        if not value or not value.strip():
            raise PreventUpdate
        term = value.strip().lower()
        # Case-insensitive mapping
        key_map = {k.lower(): k for k in TRADING_GLOSSARY.keys()}
        all_terms_lower = list(key_map.keys())
        matches = difflib.get_close_matches(term, all_terms_lower, n=1, cutoff=0.6)
        found_lower = matches[0] if matches else None
        found = key_map[found_lower] if found_lower else None
        import os
        from datetime import datetime
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        dict_dir = os.path.join(project_root, 'cache', 'dict')
        os.makedirs(dict_dir, exist_ok=True)
        no_match_file = os.path.join(dict_dir, 'no_match.txt')
        if found:
            # If the found term is not an exact match (case-insensitive), log the search
            if term != found.lower():
                with open(no_match_file, 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.now().isoformat()}\t{value.strip()}\n")
            entry = TRADING_GLOSSARY[found]
            return html.Div([
                html.H5(found, className='mb-2'),
                html.P(entry['definition'], className='mb-1'),
                html.Small(f"Example: {entry['example']}", className='text-muted'),
            ], style={'background': '#f8f9fa', 'border': '1px solid #ddd', 'borderRadius': 8, 'padding': 16, 'marginTop': 8, 'boxShadow': '0 2px 8px rgba(0,0,0,0.07)'})
        else:
            # Suggest closest match if any
            suggestion = difflib.get_close_matches(term, all_terms_lower, n=1, cutoff=0.3)
            # Store no-match or fuzzy-match search in cache/dict/no_match.txt
            with open(no_match_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()}\t{value.strip()}\n")
            if suggestion:
                suggestion_key = key_map[suggestion[0]]
                return html.Div([
                    html.P(f'No exact match found. Did you mean "{suggestion_key}"?', className='mb-1'),
                ], style={'background': '#fff3cd', 'border': '1px solid #ffeeba', 'borderRadius': 8, 'padding': 16, 'marginTop': 8})
            return html.Div([
                html.P('No definition found for this term.', className='mb-1'),
            ], style={'background': '#f8d7da', 'border': '1px solid #f5c6cb', 'borderRadius': 8, 'padding': 16, 'marginTop': 8})
