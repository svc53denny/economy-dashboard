import os
import logging
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
logger = logging.getLogger(__name__)

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        key = os.environ.get("OPENROUTER_API_KEY")
        if not key:
            raise EnvironmentError("OPENROUTER_API_KEY가 설정되지 않았습니다.")
        _client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=key,
        )
    return _client


def summarize(title: str, model: str = "openai/gpt-4o-mini") -> str | None:
    prompt = (
        "다음 경제 뉴스 제목을 읽고, 핵심 내용을 한국어로 2~3문장으로 간결하게 요약하세요.\n\n"
        f"제목: {title}"
    )
    try:
        resp = _get_client().chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error("요약 실패 [%s]: %s", title[:30], e)
        return None
