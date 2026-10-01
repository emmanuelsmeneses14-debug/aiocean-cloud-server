import asyncio
import websockets
import json
import os
import subprocess
import sys

# Configuración del servidor Cloud
SERVER_WS_URL = "wss://aiocean-cloud-core.onrender.com/ws/agent"  # Cambiar a ws://localhost:8000/ws/agent para pruebas locales
AGENT_TOKEN = "aiocean_secret_token_2026"
USER_ID = "default_user"

async def execute_local_command(action: str, target: str, payload: dict):
    """Ejecuta acciones reales en el sistema operativo local"""
    print(f"🚀 [EJECUTANDO]: Acción={action} | Target={target} | Comando='{payload.get('command')}'")
    
    # 1. Abrir VS Code
    if target == "vscode":
        try:
            if sys.platform == "win32":
                os.system("code .")
            else:
                subprocess.Popen(["code", "."])
            return {"status": "SUCCESS", "message": "VS Code abierto correctamente."}
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

    # 2. Comandos de sistema general
    elif target == "workspace":
        return {"status": "SUCCESS", "message": "Módulo Workspace procesado."}

    return {"status": "UNKNOWN_TARGET", "message": f"Target '{target}' no reconocido."}

async def run_agent():
    uri = f"{SERVER_WS_URL}?token={AGENT_TOKEN}&user_id={USER_ID}"
    print(f"🌐 Conectando al Servidor Cloud AIOCEAN en: {SERVER_WS_URL}...")

    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print("✅ [CONECTADO] Agente Local activo y listo para recibir órdenes.")
                
                while True:
                    message_raw = await websocket.recv()
                    packet = json.loads(message_raw)
                    
                    if packet.get("type") == "AUTOMATION_REQUEST":
                        action = packet.get("action")
                        target = packet.get("target")
                        payload = packet.get("payload", {})
                        
                        # Ejecutar acción local
                        result = await execute_local_command(action, target, payload)
                        
                        # Responder al servidor Cloud
                        response = {
                            "type": "AUTOMATION_RESPONSE",
                            "target": target,
                            "result": result
                        }
                        await websocket.send(json.dumps(response))

        except (websockets.exceptions.ConnectionClosed, Exception) as e:
            print(f"⚠️ Conexión perdida ({e}). Reintentando en 5 segundos...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(run_agent())