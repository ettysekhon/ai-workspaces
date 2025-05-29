from pydantic import BaseModel


class ClientMessage(BaseModel):
    role: str
    content: str


class ClientAttachment(BaseModel):
    name: str
    contentType: str  # noqa: N815
    url: str


class ToolInvocation(BaseModel):
    toolCallId: str  # noqa: N815
    toolName: str  # noqa: N815
    args: dict
    result: dict


def convert_to_deepseek_messages(messages: list[ClientMessage]):
    """
    AI-SDK sends us messages as { role, content, … }.
    DeepSeek wants [{ role, content }, …].
    """
    return [{"role": m.role, "content": m.content} for m in messages]
