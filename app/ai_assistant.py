from __future__ import annotations

from dataclasses import dataclass
from .config import settings

@dataclass(frozen=True)
class AIResult:
    text: str
    model: str
    enabled: bool

class MarselAI:
    """Optional server-side AI layer. Never exposes API credentials to the browser."""
    def __init__(self) -> None:
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model

    def health(self) -> dict:
        return {"enabled": bool(self.api_key), "model": self.model if self.api_key else None}

    def advise(self, prompt: str, context: dict | None = None) -> AIResult:
        if not self.api_key:
            return AIResult("AI-модуль не подключён в runtime. Добавьте OPENAI_API_KEY на сервере; интерфейс и API уже готовы.", self.model, False)
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        system = ("Ты AI-ассистент Ювелирной студии MARSEL. "
                  "Давай краткие практические рекомендации по ремонту, продажам, клиентскому сервису и операционной работе. "
                  "Не выдумывай цены, наличие, юридические факты или данные клиента. Если данных нет — прямо скажи, что их нет. "
                  "AI не является источником истины для бухгалтерии, склада или производственных записей.")
        payload = prompt.strip()
        if context:
            payload += "\nКонтекст (только для анализа, не источник истины): " + str(context)
        response = client.responses.create(model=self.model, instructions=system, input=payload)
        return AIResult(response.output_text, self.model, True)
