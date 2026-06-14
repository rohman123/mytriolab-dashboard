#!/usr/bin/env python3
"""MyTrioLab File Server with JSON API"""
import http.server, json, os, urllib.parse, html, mimetypes

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)

        # API endpoint for file listing
        if path == '/api/files' or path.startswith('/api/files/'):
            self.send_json(self.list_files(path.replace('/api/files', '') or '/'))
            return

        # API endpoint for file download
        if path == '/api/download':
            file_path = parsed.query.split('=', 1)[1] if '=' in parsed.query else ''
            self.serve_file(file_path)
            return

        # Serve index.html for root
        if path == '/' or path == '/index.html':
            self.serve_index()
            return

        # Default: serve static files
        super().do_GET()

    def list_files(self, subpath):
        base = os.getcwd()
        target = os.path.realpath(os.path.join(base, subpath.lstrip('/')))

        # Security: prevent directory traversal
        if not target.startswith(base):
            self.send_json({'error': 'Access denied'}, 403)
            return

        if not os.path.isdir(target):
            self.send_json({'error': 'Not a directory'}, 404)
            return

        files = []
        try:
            for f in sorted(os.listdir(target)):
                if f.startswith('.') and f != '..':
                    continue
                full = os.path.join(target, f)
                try:
                    st = os.stat(full)
                    rel_path = os.path.relpath(full, base)
                    files.append({
                        'name': f,
                        'path': rel_path,
                        'is_dir': os.path.isdir(full),
                        'size': st.st_size if not os.path.isdir(full) else 0,
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
    server = http.server.HTTPServer(('127.0.0.1', PORT), Handler)
    print(f'MyTrioLab server running on http://127.0.0.1:{PORT}')
    server.serve_forever()
