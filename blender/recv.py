# เสิร์ฟโฟลเดอร์ 3D ตลาด + รับไฟล์จากหน้าเว็บ (POST /save?name=xxx) เก็บที่ blender/<name>.glb|json|png
# ใช้ตอนส่งออกฉากไปเรนเดอร์ใน Blender เท่านั้น · ฟังแค่เครื่องนี้ (127.0.0.1)
import http.server, os, re, sys, urllib.parse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'blender')

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def do_POST(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        name = q.get('name', [''])[0]
        if not re.fullmatch(r'[a-z0-9-]{1,40}\.(glb|json|png)', name):
            self.send_error(400, 'bad name'); return
        n = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(n)
        with open(os.path.join(OUT, name), 'wb') as f: f.write(data)
        self.send_response(200); self.end_headers(); self.wfile.write(b'ok %d' % n)
        print('SAVED', name, n, flush=True)

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8791
http.server.ThreadingHTTPServer(('127.0.0.1', port), H).serve_forever()
