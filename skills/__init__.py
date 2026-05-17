from anthropic import Anthropic
from pydantic import BaseModel


def _call_structured(
    client: Anthropic,
    system: str,
    user: str,
    model_class: type[BaseModel],
    model_name: str = "claude-sonnet-4-6-default",
) -> BaseModel:
    tool_def = {
        "name": "structured_output",
        "description": "Return the structured result",
        "input_schema": model_class.model_json_schema(),
    }
    response = client.messages.create(
        model=model_name,
        max_tokens=4096,
        tools=[tool_def],
        tool_choice={"type": "tool", "name": "structured_output"},
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    tool_block = next(b for b in response.content if b.type == "tool_use")
    return model_class.model_validate(tool_block.input)
