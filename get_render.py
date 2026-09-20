import socket
import json
import base64
import sys

def get_render(view_name='iso', output_filename='fusion_render.png'):
    s = socket.socket()
    s.connect(('127.0.0.1', 9876))
    req = {'type': 'render_view', 'params': {'view': view_name, 'width': 1024, 'height': 768, 'fit': True}}
    s.sendall((json.dumps(req) + '\n').encode('utf-8'))
    s.settimeout(15)
    
    raw = b""
    while True:
        chunk = s.recv(65536)
        if not chunk:
            break
        raw += chunk
        if b'\n' in raw:
            break
    s.close()
    
    data = json.loads(raw.decode('utf-8'))
    if data.get('status') == 'success' and 'image_base64' in data.get('result', {}):
        img_bytes = base64.b64decode(data['result']['image_base64'])
        with open(output_filename, 'wb') as f:
            f.write(img_bytes)
        print(f"Render ({view_name}) saved to {output_filename}!")
    else:
        print("Error rendering:", data)

if __name__ == '__main__':
    v = sys.argv[1] if len(sys.argv) > 1 else 'iso'
    out = sys.argv[2] if len(sys.argv) > 2 else 'fusion_render.png'
    get_render(v, out)
