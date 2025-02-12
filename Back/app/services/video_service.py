# app/services/video_service.py

class VideoService:
    def __init__(self):
        self.connections = set()

    async def connect(self, websocket):
        """
        Conecta un nuevo cliente WebSocket
        """
        self.connections.add(websocket)
        try:
            await websocket.accept()
        except Exception as e:
            self.connections.remove(websocket)
            raise e

    def disconnect(self, websocket):
        """
        Desconecta un cliente WebSocket
        """
        self.connections.remove(websocket)

    async def broadcast(self, message):
        """
        Envía un mensaje a todos los clientes conectados
        """
        for connection in self.connections:
            try:
                await connection.send_json(message)
            except:
                self.connections.remove(connection)
