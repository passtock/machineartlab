import socket
import json

def test_code():
    s = socket.socket()
    s.connect(('127.0.0.1', 9876))
    code = "root = component\nres = f'{root.name}, sketches: {root.sketches.count}'\nres"
    payload = json.dumps({'type': 'execute_code', 'params': {'code': code}}) + '\n'
    s.sendall(payload.encode('utf-8'))
    s.settimeout(5)
    resp = s.recv(4096).decode('utf-8')
    s.close()
    print("Response:", resp)

if __name__ == '__main__':
    test_code()
