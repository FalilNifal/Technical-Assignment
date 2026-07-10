import json
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.ai.chat_tools import CHAT_TOOLS, execute_chat_tool
from app.ai.prompts import CHAT_SYSTEM_PROMPT
from app.core.config import settings
from app.models.user import User
from app.schemas.chat_schema import ChatRequest, ChatResponse

MAX_TOOL_ROUNDS = 6
MAX_TOKENS = 1024

# Groq uses the OpenAI function-calling shape; adapt our tool definitions once.
GROQ_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["input_schema"],
        },
    }
    for tool in CHAT_TOOLS
]


class ChatService:
    @staticmethod
    def _system_prompt() -> str:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        return CHAT_SYSTEM_PROMPT.format(today=today, week_start=week_start, week_end=week_end)

    @staticmethod
    def answer(db: Session, current_user: User, payload: ChatRequest) -> ChatResponse:
        if not settings.GROQ_API_KEY:
            return ChatResponse(
                reply=(
                    "The AI chat assistant is not configured yet. Add a GROQ_API_KEY to the "
                    "backend .env and restart the server to enable conversational answers."
                ),
                generated_by_fallback=True,
            )

        # Imported lazily so the app still boots if the SDK isn't installed.
        from groq import Groq

        client = Groq(api_key=settings.GROQ_API_KEY)
        messages: list[dict] = [{"role": "system", "content": ChatService._system_prompt()}]
        messages.extend({"role": m.role, "content": m.content} for m in payload.messages)
        tools_used: list[str] = []

        try:
            for _ in range(MAX_TOOL_ROUNDS):
                response = client.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    max_tokens=MAX_TOKENS,
                    temperature=0.2,
                    messages=messages,
                    tools=GROQ_TOOLS,
                    tool_choice="auto",
                )
                message = response.choices[0].message

                if message.tool_calls:
                    messages.append(
                        {
                            "role": "assistant",
                            "content": message.content or "",
                            "tool_calls": [
                                {
                                    "id": call.id,
                                    "type": "function",
                                    "function": {
                                        "name": call.function.name,
                                        "arguments": call.function.arguments,
                                    },
                                }
                                for call in message.tool_calls
                            ],
                        }
                    )
                    for call in message.tool_calls:
                        tools_used.append(call.function.name)
                        try:
                            args = json.loads(call.function.arguments or "{}")
                            result = execute_chat_tool(db, call.function.name, args)
                            content = json.dumps(result, default=str)
                        except Exception as error:  # surface the failure to the model, don't crash
                            content = f"Tool error: {error}"
                        messages.append(
                            {"role": "tool", "tool_call_id": call.id, "content": content}
                        )
                    continue

                reply = (message.content or "").strip()
                return ChatResponse(
                    reply=reply or "I couldn't produce an answer for that.",
                    tools_used=sorted(set(tools_used)),
                    model_name=settings.GROQ_MODEL,
                )

            return ChatResponse(
                reply="I wasn't able to finish answering that within the allowed steps. Try narrowing the question.",
                tools_used=sorted(set(tools_used)),
                model_name=settings.GROQ_MODEL,
            )
        except Exception:
            return ChatResponse(
                reply="The AI assistant is temporarily unavailable. Please try again in a moment.",
                generated_by_fallback=True,
            )
