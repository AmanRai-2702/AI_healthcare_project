
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI, APIStatusError, APIConnectionError


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_FILE)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")

BASE_URL = "https://openrouter.ai/api/v1"


def generate_response(prompt: str, max_retries: int = 3) -> str:
    """Generate a response using an OpenRouter-hosted model."""

    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt must not be empty.")

    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not configured.")

    if not OPENROUTER_MODEL:
        raise ValueError("OPENROUTER_MODEL is not configured.")

    if max_retries < 1:
        raise ValueError("max_retries must be at least 1.")

    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=BASE_URL,
        max_retries=0,
    )

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            answer = response.choices[0].message.content

            if not answer or not answer.strip():
                raise RuntimeError("OpenRouter returned an empty response.")

            return answer.strip()

        except (APIStatusError, APIConnectionError) as error:
            status_code = getattr(error, "status_code", None)

            # Retry temporary server errors and rate limits.
            if status_code not in (429, 500, 502, 503, 504) and not isinstance(
                error, APIConnectionError
            ):
                raise

            if attempt == max_retries - 1:
                raise

            time.sleep(2 ** (attempt + 1))

    raise RuntimeError("OpenRouter request failed.")
