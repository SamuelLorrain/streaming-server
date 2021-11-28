from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import io
import os

VIDEOSTREAM = "video.mp4"
CONTENT_TYPE = "video/mp4"
ADDRESS = "localhost"
PORT = 8000

class handler(BaseHTTPRequestHandler):
    videoStream = io.FileIO(VIDEOSTREAM, 'br')
    length = os.path.getsize(VIDEOSTREAM)

    def do_GET(self):
        if(self.path == '/favicon.ico'):
            self.send_error(404, "")
            return
        try:
            self.streamResponse()
        except ConnectionResetError:
            print("connection reset error")
            return
        except BrokenPipeError:
            print("connection aborted")
            return

    def streamResponse(self):
        parts = self.headers.get('Range', 'bytes=0-').replace('bytes=', '').split('-')
        start = int(parts[0])
        # compute end byte of Range request
        end = int(parts[1]) if len(parts) == 2 and parts[1] != '' else self.length - 1

        self.send_response(code=206)
        self.send_header('Content-Type', CONTENT_TYPE)
        self.send_header('Content-Length', str(self.length))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Range', f'bytes {start}-{end}/{self.length}')
        self.end_headers()
        self.videoStream.flush()
        self.videoStream.seek(start)
        chunk = self.videoStream.read(end)
        self.wfile.write(chunk)

if __name__ == '__main__':
    server = ThreadingHTTPServer(server_address=(ADDRESS, PORT), RequestHandlerClass=handler)
    server.serve_forever()
