"""Servidor local temporário (só 127.0.0.1) para entregar os mp3 à página de upload do Spotify."""
import http.server, pathlib, functools

ROOT = pathlib.Path(__file__).parent.parent / 'PRONTOS_PARA_POSTAR'


class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', 'https://creators.spotify.com')
        self.send_header('Access-Control-Allow-Private-Network', 'true')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204); self.end_headers()

    def log_message(self, *a):
        pass


http.server.ThreadingHTTPServer(('127.0.0.1', 8765), functools.partial(H, directory=str(ROOT))).serve_forever()
