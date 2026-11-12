"""Offline launcher: stable browser origin and safe repeated launches."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial
import argparse
import errno
import json
from urllib.request import ProxyHandler, build_opener
import webbrowser

ROOT = Path(__file__).resolve().parent
PORT = 8774

class LibraryHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/.movement-library-status':
            payload = json.dumps({'app': 'MovementLibrary', 'root': str(ROOT)}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(payload)
        else:
            super().do_GET()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-open', action='store_true')
    parser.add_argument('--port', type=int, default=PORT)
    args = parser.parse_args()
    url = f'http://127.0.0.1:{args.port}/index.html'
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(LibraryHandler, directory=str(ROOT)))
    except OSError as error:
        if error.errno == errno.EADDRINUSE:
            try:
                opener = build_opener(ProxyHandler({}))
                with opener.open(f'http://127.0.0.1:{args.port}/.movement-library-status', timeout=2) as response:
                    status = json.loads(response.read(8192))
                if status.get('app') == 'MovementLibrary' and status.get('root') == str(ROOT):
                    print('Movement Library 已在运行，正在打开已有页面。', flush=True)
                    if not args.no_open:
                        webbrowser.open(url)
                    return 0
            except (OSError, ValueError):
                pass
            print(f'本机地址 {args.port} 已被其他服务或另一个文件夹中的版本占用。', flush=True)
            print('请关闭原来的启动窗口后重新打开。本次未更换地址或修改资料库。', flush=True)
        else:
            print('无法启动本地页面：' + str(error), flush=True)
        return 1
    print('Movement Library 已启动：' + url, flush=True)
    print('数据保存在此浏览器本地。关闭本窗口可停止服务；重复启动会直接打开已有页面。', flush=True)
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
