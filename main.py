import asyncio
from jsonrpc import dispatcher, JSONRPCResponseManager

# Defineix una funció de prova per demostrar el funcionament
@dispatcher.add_method
def echo(message):
    return f"Echo: {message}"

class EchoServerProtocol(asyncio.Protocol):
    def __init__(self) -> None:
        self.transport = None

    def connection_made(self, transport):
        peer_name = transport.get_extra_info('peername')
        print('Connection from {}'.format(peer_name))
        self.transport = transport

    def data_received(self, data: bytes) -> None:
        message = data.decode()
        print('Data received: {!r}'.format(message))

        response = JSONRPCResponseManager.handle(message, dispatcher)
        if response:
            response_data = response.json.encode()
            print('Send response: {!r}'.format(response_data))
            self.transport.write(response_data)


async def main():
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: EchoServerProtocol(),
        '127.0.0.1', 8888)

    async with server:
        await server.serve_forever()

asyncio.run(main())
