from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

handler = SimpleHTTPRequestHandler
port = 8002  
httpd = TCPServer(("", port), handler)

print(f"Serving at port {port}")
httpd.serve_forever()
