import json

from openai import OpenAI

from app.core.config import settings


class AIClient:
    def __init__(self):
        self.model = getattr(settings, "AI_MODEL", "gpt-4o-mini")
        self.api_key = getattr(settings, "AI_API_KEY", None)

        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None

    def is_configured(self) -> bool:
        return self.client is not None

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict:
        if not self.client:
            raise RuntimeError("AI service is not configured")

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
            raise RuntimeError("AI provider returned an empty response")

        try:
            return json.loads(content)
        except json.JSONDecodeError as error:
            raise RuntimeError("AI provider returned invalid JSON") from error
