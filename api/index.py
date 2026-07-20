import sys, os
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import and run the FastAPI app
from main import app
from mangum import Mangum

# For Railway: wrap FastAPI as a handler
handler = Mangum(app)
