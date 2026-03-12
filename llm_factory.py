"""LLM Factory — 환경변수 기반으로 Gemini / OpenAI 호환 LLM 생성."""
from config import LLM_TYPE, LLM_MODEL, LLM_API_KEY, LLM_BASE_URL, LLM_TEMPERATURE


def create_llm(temperature: float | None = None):
    """LLM 인스턴스 생성.

    Args:
        temperature: 온도 (None이면 config 기본값 사용)
    """
    temp = temperature if temperature is not None else LLM_TEMPERATURE

    if LLM_TYPE == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            google_api_key=LLM_API_KEY,
            temperature=temp,
        )
    else:
        # openai / ollama / 사내 LLM — 모두 OpenAI 호환 API
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=LLM_MODEL,
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL,
            temperature=temp,
        )

    return llm
