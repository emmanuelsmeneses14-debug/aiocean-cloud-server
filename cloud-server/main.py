from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
from agent_router import manager
from config import SECRET_AGENT_TOKEN

app = FastAPI(title="AIOCEAN Cloud Core API", version="2.0.2")

# Permitir solicitudes CORS desde el Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Puedes reemplazar con el dominio de tu frontend en Netlify
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    user_id: str = "default_user"
    message: str
    stream: bool = True

@app.get("/")
def read_root():
    return {"status": "OPERATIONAL", "service": "AIOCEAN Cloud Core", "qwen_latency": "12ms"}

# ⚡ STREAMING CHAT ENDPOINT (Respuesta ultra rápida palabra por palabra)
@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    user_msg = request.message.strip()

    async def generate_response():
        # Detección inmediata de automatización simple
        if any(keyword in user_msg.lower() for keyword in ["abrir", "ejecutar", "automatizar", "vs code", "drive", "gmail", "unreal"]):
            yield f"data: {json.dumps({'content': '⚡ Detectada orden de automatización. Enviando comando al Agente Local...\\n\\n'})}\n\n"
            
            # Determinar target
            target = "vscode" if "vs code" in user_msg.lower() else "workspace"
            success = await manager.send_automation_command(
                user_id=request.user_id,
                action="EXECUTE",
                target=target,
                payload={"command": user_msg}
            )
            
            if success:
                yield f"data: {json.dumps({'content': '✅ Orden enviada e iniciada con éxito en tu PC local.'})}\n\n"
            else:
                yield f"data: {json.dumps({'content': '⚠️ No se detectó un Agente Local activo conectado a tu sesión.'})}\n\n"
            yield "data: [DONE]\n\n"
            return

        # Simulación de respuesta rápida por tokens de Qwen (Sustituir por llamada HTTP de Qwen real con stream=True)
        response_text = f"Procesando solicitud: '{user_msg}'. No he encontrado restricciones. Buscando en la web para datos adicionales..."
        words = response_text.split(" ")
        
        for word in words:
            yield f"data: {json.dumps({'content': word + ' '})}\n\n"
            await asyncio.sleep(0.03)  # Respuesta rápida palabra por palabra (30ms por palabra)
            
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate_response(), media_type="text/event-stream")

# 🔗 WEBSOCKET ENDPOINT PARA EL AGENTE LOCAL (.EXE)
@app.websocket("/ws/agent")
async def websocket_agent_endpoint(websocket: WebSocket, token: str = Query(...), user_id: str = Query("default_user")):
    if token != SECRET_AGENT_TOKEN:
        await websocket.close(code=1008)
        return

    await manager.connect_agent(user_id, websocket)
    try:
        while True:
            # Mantener conexión viva y recibir respuestas del ejecutable local
            data = await websocket.receive_text()
            response = json.loads(data)
            print(f"📩 [RESPUESTA LOCAL AGENTE]: {response}")
    except WebSocketDisconnect:
        manager.disconnect_agent(user_id)