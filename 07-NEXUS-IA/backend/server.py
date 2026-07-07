from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os

class NexusHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/estado':
            data = {
                "estado": "ok",
                "mensaje": "Nexus IA en servidor local (Fase 1)"
            }
            response = json.dumps(data).encode('utf-8')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response)))
            self.end_headers()
            self.wfile.write(response)
        else:
            if self.path == '/':
                path = 'index.html'
            else:
                path = self.path.lstrip('/')

            file_path = os.path.join('frontend', path)

            if os.path.isfile(file_path):
                if file_path.endswith('.html'):
                    content_type = 'text/html'
                elif file_path.endswith('.css'):
                    content_type = 'text/css'
                elif file_path.endswith('.js'):
                    content_type = 'application/javascript'
                else:
                    content_type = 'application/octet-stream'

                with open(file_path, 'rb') as f:
                    content = f.read()

                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Not Found')

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.chdir('..')

    server_address = ('0.0.0.0', 8000)
    httpd = HTTPServer(server_address, NexusHandler)
    print("Nexus IA servidor local escuchando en http://0.0.0.0:8000")
    httpd.serve_forever()
