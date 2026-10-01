import os
from dotenv import load_dotenv

load_dotenv()

# Puerto y entorno
PORT = int(os.getenv("PORT", 8000))

# API Keys para modelos (Qwen / Gemini / Claude)
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
QWEN_API_BASE = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1") # O endpoint de Together/Groq/OpenRouter
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Token de autenticación básico para conectar el agente local de forma segura
SECRET_AGENT_TOKEN = os.getenv("SECRET_AGENT_TOKEN", "aiocean_secret_token_2026")