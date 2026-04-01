from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.rooms: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket:WebSocket, room: str):
        await websocket.accept()
        if room not in self.rooms:
            self.rooms[room]=[]
        self.rooms[room].append(websocket)

    def disconnect(self, websocket:WebSocket, room: str):
        if room in self.rooms:
            try:
                self.rooms[room].remove(websocket)
            except ValueError:
                pass
            if not self.rooms[room]:
                del self.rooms[room]

    async def broadcast(self, room: str, message: dict):
        if room not in self.rooms:
            return
        dead=[]
        for connection in self.rooms[room]:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for connection in dead:
            self.rooms[room].remove(connection)

manager = ConnectionManager()