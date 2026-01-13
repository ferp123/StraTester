
def get_date_range_from_cache(symbol, provider, timeframe):
    """
    This file is now a launcher for the modular dashboard app.
    All dashboard code has been migrated to the src/dashboard/ subpackage.
    You can still launch the dashboard using: python src/dashboard.py
    """


import os
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys

if __name__ == "__main__":
    print("[dashboard.py] Starting dashboard launcher...")
    this_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(this_dir, '..'))
    print(f"[dashboard.py] Current working directory before chdir: {os.getcwd()}")
    os.chdir(project_root)
    print(f"[dashboard.py] Changed working directory to project root: {project_root}")
    # Ensure src/ is in sys.path so absolute imports work
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    if os.path.join(project_root, 'src') not in sys.path:
        sys.path.insert(0, os.path.join(project_root, 'src'))
    print(f"[dashboard.py] sys.path: {sys.path}")
    from dashboard.app import app
    print("[dashboard.py] Imported dashboard.app.app successfully.")
    print("[dashboard.py] Launching Dash app...")
    app.run(debug=True)
