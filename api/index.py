from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "message": "Quirrely API v2.0", 
            "status": "running",
            "path": self.path
        }
        self.wfile.write(json.dumps(response).encode())
        
    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Simple mock analysis response
        response = {
            "profile": {
                "primary": "assertive",
                "secondary": "open"
            },
            "confidence": 0.85,
            "suggestions": [
                "Your writing shows strong assertive patterns",
                "Consider varying your sentence structure"
            ]
        }
        self.wfile.write(json.dumps(response).encode())