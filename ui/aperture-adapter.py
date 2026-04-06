"""OpenAI-to-Anthropic format adapter proxy.

Receives OpenAI /v1/chat/completions requests,
converts to Anthropic /v1/messages format,
forwards to Aperture, returns OpenAI format response.
"""
import json
import os
import time
import uuid

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse

app = FastAPI()

APERTURE_BASE = os.getenv("APERTURE_BASE", "http://100.118.111.59")
API_KEY = os.getenv("APERTURE_API_KEY", "")


def _oai_to_anthropic(body: dict) -> dict:
    """OpenAI Chat Completions → Anthropic Messages"""
    messages = []
    system = None
    for msg in body.get("messages", []):
        role = msg["role"]
        content = msg["content"]
        if role == "system":
            system = content
        elif role == "tool":
            messages.append({"role": "user", "content": f"Tool result: {content}"})
        elif role == "assistant":
            messages.append({"role": "assistant", "content": content})
        else:
            messages.append({"role": role, "content": content})

    out = {
        "model": body.get("model", "glm-5.1"),
        "messages": messages,
        "max_tokens": body.get("max_tokens", 4096),
    }
    if system:
        out["system"] = system
    if body.get("stream"):
        out["stream"] = True
    return out


def _anthropic_to_oai(data: dict, model: str) -> dict:
    """Anthropic Messages response → OpenAI Chat Completions response"""
    content = ""
    if data.get("content"):
        for block in data["content"]:
            if block.get("type") == "text":
                content += block["text"]

    return {
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": data.get("stop_reason", "stop") or "stop",
        }],
        "usage": {
            "prompt_tokens": data.get("usage", {}).get("input_tokens", 0),
            "completion_tokens": data.get("usage", {}).get("output_tokens", 0),
            "total_tokens": data.get("usage", {}).get("input_tokens", 0)
                         + data.get("usage", {}).get("output_tokens", 0),
        },
    }


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    anthropic_body = _oai_to_anthropic(body)
    model = body.get("model", "glm-5.1")

    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    if body.get("stream"):
        return StreamingResponse(
            _stream_convert(anthropic_body, headers, model),
            media_type="text/event-stream",
        )

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{APERTURE_BASE}/v1/messages",
            json=anthropic_body,
            headers=headers,
        )
        if resp.status_code != 200:
            return JSONResponse(content=resp.json(), status_code=resp.status_code)
        return _anthropic_to_oai(resp.json(), model)


async def _stream_convert(anthropic_body: dict, headers: dict, model: str):
    """Convert Anthropic SSE stream → OpenAI SSE stream"""
    import asyncio

    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream(
            "POST",
            f"{APERTURE_BASE}/v1/messages",
            json=anthropic_body,
            headers=headers,
        ) as resp:
            msg_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
            created = int(time.time())
            buffer = ""

            async for raw in resp.aiter_text():
                buffer += raw
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line or not line.startswith("data: "):
                        continue
                    payload = line[6:]
                    if payload == "[DONE]":
                        yield "data: [DONE]\n\n"
                        return
                    try:
                        evt = json.loads(payload)
                    except json.JSONDecodeError:
                        continue

                    event_type = evt.get("type", "")

                    if event_type == "content_block_delta":
                        delta = evt.get("delta", {})
                        text = delta.get("text", "")
                        if text:
                            chunk = {
                                "id": msg_id,
                                "object": "chat.completion.chunk",
                                "created": created,
                                "model": model,
                                "choices": [{
                                    "index": 0,
                                    "delta": {"content": text},
                                    "finish_reason": None,
                                }],
                            }
                            yield f"data: {json.dumps(chunk)}\n\n"

                    elif event_type == "message_stop":
                        chunk = {
                            "id": msg_id,
                            "object": "chat.completion.chunk",
                            "created": created,
                            "model": model,
                            "choices": [{
                                "index": 0,
                                "delta": {},
                                "finish_reason": "stop",
                            }],
                        }
                        yield f"data: {json.dumps(chunk)}\n\n"
                        yield "data: [DONE]\n\n"
                        return


@app.get("/v1/models")
async def list_models():
    """Passthrough to Aperture"""
    headers = {"x-api-key": API_KEY, "anthropic-version": "2023-06-01"}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{APERTURE_BASE}/v1/models", headers=headers)
        return resp.json()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
