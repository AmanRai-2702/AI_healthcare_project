
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError


PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_FILE)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")


def generate_response(prompt: str, max_retries: int = 3) -> str:
    """Generate a response using Gemini with limited retries."""

    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt must not be empty.")

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured.")

    if max_retries < 1:
        raise ValueError("max_retries must be at least 1.")

    client = genai.Client(api_key=GEMINI_API_KEY)

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )

            if not response.text:
                raise RuntimeError("Gemini returned an empty response.")

            return response.text.strip()

        except APIError as error:
            # Retry only temporary overload or rate-limit errors.
            if error.code not in (429, 503):
                raise

            if attempt == max_retries - 1:
                raise

            wait_seconds = 2 ** (attempt + 1)
            time.sleep(wait_seconds)

    raise RuntimeError("Gemini request failed.")
