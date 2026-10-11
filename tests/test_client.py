"""One-image Qwen request and terminal-result boundaries."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from client import QwenImageClient, QwenImageError


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.headers = {"x-trace-id": "trace-qwen"}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, *_):
        return json.dumps(self.payload).encode()


@pytest.mark.asyncio
async def test_submit_sends_one_async_image_request():
    calls = []

    def fake_open(request, timeout):
        calls.append((request.full_url, json.loads(request.data), timeout))
        return FakeResponse({"task_id": "task-123"})

    with patch("client.OPENER.open", side_effect=fake_open):
        result = await QwenImageClient("test-key").submit("A ceramic vase")
    assert calls == [
        (
            "https://api.acedata.cloud/qwen-image/images",
            {
                "model": "qwen-image-3.0",
                "prompt": "A ceramic vase",
                "n": 1,
                "size": "1024*1024",
                "watermark": False,
                "async": True,
            },
            90,
        )
    ]
    assert result["status"] == "submitted"
    assert result["task_id"] == "task-123"
    assert "image_urls" not in result


@pytest.mark.asyncio
async def test_edit_sends_only_authorized_https_reference():
    with patch(
        "client.OPENER.open", return_value=FakeResponse({"task_id": "task-456"})
    ) as opening:
        await QwenImageClient("test-key").submit(
            "Make it blue", image_url="https://example.org/vase.jpg"
        )
    payload = json.loads(opening.call_args.args[0].data)
    assert payload["image_urls"] == ["https://example.org/vase.jpg"]


@pytest.mark.asyncio
async def test_task_lookup_withholds_preview_and_keeps_public_cost():
    submitted = {"id": "task-123", "trace_id": "trace-qwen"}
    preview = {
        "finished_at": None,
        "response": {
            "success": True,
            "data": [{"image_url": "https://cdn.example.org/preview.png"}],
        },
    }
    finished = {
        "finished_at": 123.0,
        "response": {
            "success": True,
            "data": [{"image_url": "https://cdn.example.org/final.png"}],
            "cost": {
                "amount": 0.28,
                "list_amount": 0.31,
                "currency": "credit",
                "supplier": "internal-only",
            },
        },
    }
    with patch(
        "client.OPENER.open",
        side_effect=[
            FakeResponse(submitted),
            FakeResponse(preview),
            FakeResponse(finished),
        ],
    ) as opening:
        first = await QwenImageClient("test-key").query("task-123")
        second = await QwenImageClient("test-key").query("task-123")
        last = await QwenImageClient("test-key").query("task-123")
    assert opening.call_count == 3
    assert first["status"] == "pending"
    assert first["image_urls"] == []
    assert second["status"] == "pending"
    assert second["image_urls"] == []
    assert last["status"] == "succeeded"
    assert last["image_urls"] == ["https://cdn.example.org/final.png"]
    assert last["cost"] == {
        "amount": 0.28,
        "list_amount": 0.31,
        "currency": "credit",
    }
    assert "supplier" not in str(last)


@pytest.mark.asyncio
async def test_invalid_input_never_submits_a_paid_job():
    with patch("client.OPENER.open") as opening, pytest.raises(QwenImageError):
        await QwenImageClient("test-key").submit(" ")
    assert opening.call_count == 0
    with patch("client.OPENER.open") as opening, pytest.raises(QwenImageError):
        await QwenImageClient("test-key").submit("A vase", model="unknown")
    assert opening.call_count == 0
    with patch("client.OPENER.open") as opening, pytest.raises(QwenImageError):
        await QwenImageClient("test-key").submit(
            "A vase", image_url="http://example.org/vase.jpg"
        )
    assert opening.call_count == 0
