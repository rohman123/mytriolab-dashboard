#!/usr/bin/env python3
"""MyTrioLab File Server with JSON API"""
import http.server, json, os, urllib.parse, mimetypes

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)

        if path == '/api/files' or path.startswith('/api/files/'):
            self.list_files(path.replace('/api/files', '') or '/')
            return

        if path.startswith('/api/download'):
            params = dict(urllib.parse.parse_qsl(parsed.query))
            self.serve_file(params.get('path', ''))
            return

        if path == '/' or path == '/index.html':
            self.serve_index()
            return

        super().do_GET()

    def list_files(self, subpath):
        base = os.getcwd()
        target = os.path.realpath(os.path.join(base, subpath.lstrip('/'))) if subpath != '/' else base

        if not target.startswith(base):
            self.send_json({'error': 'Access denied'}, 403)
            return

        if not os.path.isdir(target):
            self.send_json({'error': 'Not a directory'}, 404)
            return

        files = []
        try:
            for f in sorted(os.listdir(target), key=lambda x: x.lower()):
                if f.startswith('.'):
                    continue
                full = os.path.join(target, f)
                try:
                    st = os.stat(full)
                    is_dir = os.path.isdir(full)
                    rel_path = os.path.relpath(full, base)
                    files.append({
                        'name': f,
                        'path': rel_path,
                        'isDir': is_dir,          # camelCase agar cocok dengan JS
                        'size': 0 if is_dir else st.st_size,
                        'mtime': int(st.st_mtime),
                    })
                except OSError:
                    continue
        except PermissionError:
            self.send_json({'error': 'Permission denied'}, 403)
            return

        self.send_json({'cwd': subpath, 'files': files})

    def serve_index(self):
        index_path = os.path.join(os.getcwd(), 'index.html')
        if os.path.exists(index_path):
            with open(index_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_json({'error': 'index.html not found'}, 404)

    def serve_file(self, file_path):
        base = os.getcwd()
        if not file_path:
            self.send_json({'error': 'No path specified'}, 400)
            return
        target = os.path.realpath(os.path.join(base, file_path))
        if not target.startswith(base) or not os.path.isfile(target):
            self.send_json({'error': 'File not found'}, 404)
            return
        content_type, _ = mimetypes.guess_type(target)
        content_type = content_type or 'application/octet-stream'
        with open(target, 'rb') as f:
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(target)}"')
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # Suppress logs

if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    print(f'MyTrioLab server running on http://0.0.0.0:{PORT}')
    server.serve_forever()