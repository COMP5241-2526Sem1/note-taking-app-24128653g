"""
Vercel serverless entrypoint. Exposes the Flask `app` from src.main as a WSGI application
that the Vercel Python builder can invoke.

Vercel's Python runtime will look for a WSGI callable named `app` in this module.
"""
import os
import sys

# Ensure project root is on path (main.py expects src on sys.path via its own insertion)
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src import main as app_module

# The Flask app instance
app = app_module.app

# If you need to run any initialization here, ensure environment vars are present.
# The app in src/main.py already raises if MONGODB_URI is not set.

if __name__ == "__main__":
    # Local dev run
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)), debug=True)
