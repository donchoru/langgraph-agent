import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "logistics.db"
TRACES_DIR = BASE_DIR / "traces"

# LLM 설정 — 환경변수로 백엔드 전환
# LLM_TYPE: "gemini" (기본) | "openai" (OpenAI 호환 — 사내 LLM, Ollama 등)
LLM_TYPE = os.getenv("LLM_TYPE", "gemini")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")
LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("GEMINI_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")  # OpenAI 호환 시 필수
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))

# 하위 호환
GEMINI_API_KEY = LLM_API_KEY
GEMINI_MODEL = LLM_MODEL
