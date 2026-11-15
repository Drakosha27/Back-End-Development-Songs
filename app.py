"""Runnable local Songs API demo using only Python's standard library."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from urllib.parse import urlparse
songs = {1: {'id':1, 'title':'Demo Song', 'artist':'Demo Artist'}}
next_id = 2
class Handler(BaseHTTPRequestHandler):
    def send_json(self, code, obj):
        raw=json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length', str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)
    def payload(self): return json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))) or b'{}')
    def sid(self):
        try: return int(urlparse(self.path).path.rsplit('/', 1)[1])
        except ValueError: return -1
    def do_GET(self):
        path=urlparse(self.path).path
        if path=='/health': return self.send_json(200, {'status':'OK'})
        if path=='/count': return self.send_json(200, {'count':len(songs)})
        if path=='/song': return self.send_json(200, list(songs.values()))
        if path.startswith('/song/'):
            song=songs.get(self.sid())
            return self.send_json(200 if song else 404, song or {'error':'not found'})
        return self.send_json(404, {'error':'not found'})
    def do_POST(self):
        global next_id
        if urlparse(self.path).path!='/song': return self.send_json(404, {'error':'not found'})
        data=self.payload(); data['id']=next_id; songs[next_id]=data; next_id+=1
        return self.send_json(201, data)
    def do_PUT(self):
        sid=self.sid()
        if sid not in songs: return self.send_json(404, {'error':'not found'})
        songs[sid].update(self.payload()); songs[sid]['id']=sid
        return self.send_json(200, songs[sid])
    def do_DELETE(self):
        sid=self.sid()
        if sid not in songs: return self.send_json(404, {'error':'not found'})
        del songs[sid]; return self.send_json(200, {'deleted':sid})
if __name__ == '__main__':
    print('Songs service: http://127.0.0.1:5002', flush=True)
    ThreadingHTTPServer(('127.0.0.1',5002),Handler).serve_forever()
