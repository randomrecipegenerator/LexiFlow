import sys, os, json

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

def app(environ, start_response):
    path = environ.get("PATH_INFO", "")
    status = "200 OK"
    headers = [("Content-Type", "application/json")]
    
    if path == "/api/health":
        body = json.dumps({"status": "healthy", "message": "WSGI test"}).encode()
    else:
        status = "500 Internal Server Error"
        body = json.dumps({"error": "Not implemented"}).encode()
    
    start_response(status, headers)
    return [body]