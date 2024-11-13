import socket
import json

def jsonrpc_request(method: str, params: dict, id: int|str):
    return json.dumps({
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": id
    }).encode()

def test_echo_server():
    with socket.create_connection(("127.0.0.1", 8888)) as sock:
        request = jsonrpc_request("echo", {"message": "Howdy"}, 1)
        sock.sendall(request)

        response = sock.recv(1024)
        assert response.decode() == '{"result": "Echo: Howdy", "id": 1, "jsonrpc": "2.0"}'
