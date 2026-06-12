from main import app
for route in app.routes:
    print(f"Path: {route.path}, Name: {route.name}, Methods: {route.methods if hasattr(route, 'methods') else 'N/A'}")
    if hasattr(route, "app") and hasattr(route.app, "routes"):
        for sub_route in route.app.routes:
            print(f"  Sub-Path: {sub_route.path}, Name: {sub_route.name}, Methods: {sub_route.methods if hasattr(sub_route, 'methods') else 'N/A'}")
