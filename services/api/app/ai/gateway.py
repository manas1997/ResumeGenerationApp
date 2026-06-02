from typing import Any, Protocol

from pydantic import BaseModel, ValidationError


class AIProvider(Protocol):
    def structured_completion(
        self,
        *,
        prompt_name: str,
        system_prompt: str,
        user_payload: dict[str, Any],
        schema: type[BaseModel],
    ) -> BaseModel:
        """Return a schema-validated response from an AI provider."""


class SchemaValidationError(RuntimeError):
    pass


def validate_structured_output(schema: type[BaseModel], payload: dict[str, Any]) -> BaseModel:
    try:
        return schema.model_validate(payload)
    except ValidationError as exc:
        raise SchemaValidationError(str(exc)) from exc

