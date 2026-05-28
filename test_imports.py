import sys, os
backend_path = os.path.join(os.getcwd(), "backend")
sys.path.append(backend_path)
print(f"sys.path appended: {backend_path}")
try:
    import backend.models as bm
    print("Imported backend.models")
except ImportError as e:
    print(f"Failed to import backend.models: {e}")

try:
    import models as m
    print("Imported models")
except ImportError as e:
    print(f"Failed to import models: {e}")

if 'bm' in locals() and 'm' in locals():
    print(f"bm is m: {bm is m}")
    print(f"bm name: {bm.__name__}")
    print(f"m name: {m.__name__}")
