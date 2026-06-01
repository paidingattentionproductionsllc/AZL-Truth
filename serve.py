import http.server
import socketserver
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>AZL Universe Map v2.0</title>
<style>
  body { margin:0; background:#030318; display:flex; flex-direction:column;
         align-items:center; justify-content:flex-start; min-height:100vh; }
  h1   { color:#CCCCEE; font-family:monospace; font-size:13px; margin:10px 0 4px;
         text-align:center; }
  p    { color:#7777AA; font-family:monospace; font-size:10px; margin:0 0 8px;
         text-align:center; }
  img  { max-width:100%; height:auto; display:block; }
</style>
</head>
<body>
<h1>AZL UNIVERSE MAP v2.0 — 5D OBSERVABLE REALITY</h1>
<p>D1/D2/D3 = Space (Mpc) &nbsp;|&nbsp; D4 = Lookback Time / Color &nbsp;|&nbsp;
   D5 = log(Mass/M&#9737;) / Size &nbsp;|&nbsp;
   Cyan=DARK N&#xd7;0=N &nbsp;|&nbsp; Gold=LIGHT 1&#xd7;N=N+1 &nbsp;|&nbsp;
   Purple=VOID 0&#xd7;N=0</p>
<img src="/universe_map.png" alt="AZL Universe Map">
</body>
</html>"""

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", ""):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(HTML.encode())))
            self.end_headers()
            self.wfile.write(HTML.encode())
        else:
            super().do_GET()

    def log_message(self, format, *args):
        pass

PORT = 5000
with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"AZL Universe Map serving on port {PORT}")
    httpd.serve_forever()
