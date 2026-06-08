import json
from typing import Any

from pydantic import BaseModel


class OpenAIProviderError(RuntimeError):
    pass


class OpenAIProvider:
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        timeout_seconds: float,
        max_retries: int,
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise OpenAIProviderError("OpenAI SDK is not installed.") from exc

        self._client = OpenAI(
            api_key=api_key,
            timeout=timeout_seconds,
            max_retries=max_retries,
        )
        self._model = model

    def structured_completion(
        self,
        *,
        prompt_name: str,
        system_prompt: str,
        user_payload: dict[str, Any],
        schema: type[BaseModel],
    ) -> BaseModel:
        try:
            response = self._client.responses.parse(
                model=self._model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": (
                            f"Prompt: {prompt_name}\n"
                            f"Return JSON matching the requested schema.\n"
                            f"Payload:\n{json.dumps(user_payload, ensure_ascii=False)}"
                        ),
                    },
                ],
                text_format=schema,
            )
        except Exception as exc:
            raise OpenAIProviderError("OpenAI structured completion failed.") from exc

        parsed = getattr(response, "output_parsed", None)
        if parsed is None:
            raise OpenAIProviderError("OpenAI response did not include parsed structured output.")
        if isinstance(parsed, schema):
            return parsed
        return schema.model_validate(parsed)

