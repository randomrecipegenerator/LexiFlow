
import sys
import os

# Add root directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

print(f"Current dir: {current_dir}")
print(f"Root dir: {root_dir}")
print(f"Sys path: {sys.path[:3]}")

try:
    from main import app
    print("Successfully imported app from main")
    print(f"Routes: {[route.path for route in app.routes if hasattr(route, 'path')]}")
except Exception as e:
    print(f"Failed to import app: {e}")
