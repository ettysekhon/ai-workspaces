import asyncio
import json
import logging
import uuid
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from pydantic import BaseModel

from deepseek_api.prompt import ClientMessage
from deepseek_api.settings import DEEPSEEK_API_KEY

from .prompt import convert_to_deepseek_messages


class CustomFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = "N/A"
        return super().format(record)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5s [%(request_id)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = CustomFormatter(
    fmt="%(asctime)s %(levelname)-5s [%(request_id)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
handler.setFormatter(formatter)
logger.handlers = [handler]

if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY environment variable is not set")

deepseek_client = AsyncOpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1",
)

router = APIRouter()


class ChatRequest(BaseModel):
    messages: list[ClientMessage]
    model: str = "deepseek-chat"
    stream: bool = False
    temperature: float = 0.5
    max_tokens: int = 2048
    request_id: str | None = None


async def stream_generator(
    stream: AsyncGenerator, request_id: str, model: str
) -> AsyncGenerator[str, None]:
    """
    Generate SSE events from the DeepSeek stream, with chunk aggregation and a single step.
    Handles reasoning_content for deepseek-reasoner model.
    """
    buffer = ""
    reasoning_buffer = ""
    buffer_timeout = 0.5
    last_yield_time = asyncio.get_event_loop().time()
    is_reasoner = model == "deepseek-reasoner"

    logger.info(
        f"Starting stream for request_id: {request_id}",
        extra={"request_id": request_id},
    )

    yield f"data: {json.dumps({'type': 'start'})}\n\n"
    yield f"data: {json.dumps({'type': 'start-step'})}\n\n"

    try:
        async for chunk in stream:
            logger.info(f"Full chunk: {chunk}", extra={"request_id": request_id})
            for choice in chunk.choices:
                if choice.finish_reason == "stop":
                    logger.info(
                        "Received stop signal", extra={"request_id": request_id}
                    )
                    if is_reasoner and reasoning_buffer:
                        event = {"type": "reasoning", "text": reasoning_buffer}
                        yield f"data: {json.dumps(event)}\n\n"
                        reasoning_buffer = ""
                    if buffer:
                        event = {"type": "text", "text": buffer}
                        yield f"data: {json.dumps(event)}\n\n"
                        buffer = ""
                    yield f"data: {json.dumps({'type': 'finish-step'})}\n\n"
                    yield f"data: {json.dumps({'type': 'finish'})}\n\n"
                    break

                if is_reasoner:
                    reasoning_content = getattr(choice.delta, "reasoning_content", None)
                    if reasoning_content:
                        logger.info(
                            f"Received reasoning_content: {reasoning_content}",
                            extra={"request_id": request_id},
                        )
                        reasoning_buffer += reasoning_content

                        current_time = asyncio.get_event_loop().time()
                        should_flush_reasoning = (
                            any(reasoning_buffer.endswith(char) for char in ".!?")
                            or "\n\n" in reasoning_buffer
                            or (current_time - last_yield_time) >= buffer_timeout
                        )

                        if should_flush_reasoning and reasoning_buffer:
                            event = {"type": "reasoning", "text": reasoning_buffer}
                            yield f"data: {json.dumps(event)}\n\n"
                            logger.info(
                                f"Yielded reasoning content: {reasoning_buffer}",
                                extra={"request_id": request_id},
                            )
                            reasoning_buffer = ""
                            last_yield_time = current_time

                content = getattr(choice.delta, "content", None)
                if content:
                    logger.info(
                        f"Received content: {content}", extra={"request_id": request_id}
                    )
                    buffer += content

                    current_time = asyncio.get_event_loop().time()
                    should_flush = (
                        any(buffer.endswith(char) for char in ".!?")
                        or "\n\n" in buffer
                        or (current_time - last_yield_time) >= buffer_timeout
                    )

                    if should_flush and buffer:
                        logger.info(
                            f"Buffer before flush: {buffer}",
                            extra={"request_id": request_id},
                        )
                        event = {"type": "text", "text": buffer}
                        yield f"data: {json.dumps(event)}\n\n"
                        logger.info(
                            f"Yielded buffered content: {buffer}",
                            extra={"request_id": request_id},
                        )
                        buffer = ""
                        last_yield_time = current_time
                else:
                    logger.info(
                        "No content in chunk.delta", extra={"request_id": request_id}
                    )

            yield ""
    except Exception as e:
        logger.error(f"Error in stream: {str(e)}", extra={"request_id": request_id})
        error_event = {"type": "error", "errorText": "An error occurred."}
        yield f"data: {json.dumps(error_event)}\n\n"
        raise


@router.post("/chat/completions")
async def chat_completions(request: ChatRequest):
    """Handle chat completions with DeepSeek API, returning AI-SDK-compatible SSE stream."""
    request_id = request.request_id or str(uuid.uuid4())
    logger.info(
        f"Processing request with request_id: {request_id}",
        extra={"request_id": request_id},
    )

    try:
        deepseek_messages = convert_to_deepseek_messages(request.messages)
        logger.info(
            f"DeepSeek messages: {deepseek_messages}", extra={"request_id": request_id}
        )

        if request.stream:
            stream = await deepseek_client.chat.completions.create(
                model=request.model,
                messages=deepseek_messages,
                stream=True,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

            response = StreamingResponse(
                stream_generator(stream, request_id, request.model),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                    "x-vercel-ai-data-stream": "v1",
                },
            )
            return response
        else:
            response = await deepseek_client.chat.completions.create(
                model=request.model,
                messages=deepseek_messages,
                stream=False,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            logger.info(
                f"Non-streaming response: {response}", extra={"request_id": request_id}
            )
            return response.model_dump()

    except Exception as e:
        logger.error(
            f"Error in chat completion: {str(e)}", extra={"request_id": request_id}
        )
        raise HTTPException(status_code=500, detail=str(e)) from e
