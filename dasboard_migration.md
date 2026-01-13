Dashboard Modularization & Migration Plan

1. Create the New Folder Structure
   src/
   dashboard/
   **init**.py
   app.py # Entry point: app init, layout, callback registration
   layout.py # Main layout definition
   callbacks.py # All callback functions (or split by feature)
   utils.py # Helper functions (formatting, data, etc.)
   state.py # (Optional) Global/session state management
   components/
   **init**.py
   metrics_panel.py
   trade_table.py
   performance_charts.py
   ... (other components)
2. Move Dashboard Code
   Move all dashboard-related code from src/ into src/dashboard/ as per the structure above.
3. Update All Import Paths
   Update all imports in the dashboard code to use relative imports (e.g., from .components.metrics_panel import metrics_panel).
   Update any other codebases (CLI, tests, etc.) that import from the dashboard to use the new path (e.g., from src.dashboard.app import app).
   Search the entire codebase for any references to the old dashboard.py location and update them.
4. Refactor and Test Incrementally
   After each move, run the app and tests to ensure nothing is broken.
   Fix any import or path errors as they arise.
5. Update Documentation and Scripts
   Update README, run scripts, and any documentation to reference the new dashboard entry point (src/dashboard/app.py).
6. Commit and Push
   Once everything is working, commit the changes and push to your repository.
