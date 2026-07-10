import json

from app.core.config import settings


class GroqJSONClient:
    """Thin wrapper over the Groq SDK that returns a parsed JSON object.

    Groq is OpenAI-compatible, so this uses chat.completions with JSON mode.
    The prompt must mention "JSON" for json_object mode to be accepted.
    """

    def __init__(self):
        self.model = settings.GROQ_MODEL
        self.api_key = settings.GROQ_API_KEY
        self.client = None

        if self.api_key:
            from groq import Groq

            self.client = Groq(api_key=self.api_key)

    def is_configured(self) -> bool:
        return self.client is not None

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict:
        if not self.client:
            raise RuntimeError("Groq is not configured")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError("Groq returned an empty response")

        try:
            return json.loads(content)
        except json.JSONDecodeError as error:
            raise RuntimeError("Groq returned invalid JSON") from error
