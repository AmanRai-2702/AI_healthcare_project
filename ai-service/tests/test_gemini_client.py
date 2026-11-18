
import os
import pytest

from app.llm.gemini_client import generate_response


@pytest.mark.skipif(
    os.getenv("RUN_GEMINI_INTEGRATION") != "1",
    reason="Set RUN_GEMINI_INTEGRATION=1 to run the live Gemini API test.",
)
def test_gemini_generates_response():
    response = generate_response(
        "Reply with exactly: Hello from MedFusion AI."
    )

    assert isinstance(response, str)
    assert len(response) > 0
    assert "Hello" in response
