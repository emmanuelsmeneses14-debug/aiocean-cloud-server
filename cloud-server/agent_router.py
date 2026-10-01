from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

class ConnectionManager:
    def __init__(self):
        # Conexiones activas de agentes locales indexadas por ID de usuario
        self.active_agents: Dict[str, WebSocket] = {}

    async def connect_agent(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_agents[user_id] = websocket
        print(f"🟢 [WEBSOCKET] Agente Local conectado para el usuario: {user_id}")

    def disconnect_agent(self, user_id: str):
        if user_id in self.active_agents:
            del self.active_agents[user_id]
            print(f"🔴 [WEBSOCKET] Agente Local desconectado para: {user_id}")

    async def send_automation_command(self, user_id: str, action: str, target: str, payload: dict):
        """Envia un comando de automatización directa al ejecutable local"""
        if user_id in self.active_agents:
            ws = self.active_agents[user_id]
            command_packet = {
                "type": "AUTOMATION_REQUEST",
                "action": action,
                "target": target,
                "payload": payload
            }
            await ws.send_text(json.dumps(command_packet))
            return True
        else:
            print(f"⚠️ [WEBSOCKET] El agente local para {user_id} no está conectado.")
            return False

manager = ConnectionManager()