from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

form = '''<!DOCTYPE html>
<html lang="en">
<body>
    <form method="POST" action="http://localhost:8000/"></form>
    <h1>hello</h1>
</body>
</html>
'''


class MessageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(form.encode())


if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MessageHandler)
    httpd.serve_forever()
