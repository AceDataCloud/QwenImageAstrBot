"""Single-image Qwen Image submission and task lookup for AstrBot."""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

API_BASE = "https://api.acedata.cloud"
MODELS = {"qwen-image-3.0", "qwen-image-3.0-pro"}
SIZE_PATTERN = re.compile(r"^(\d{3,4})\*(\d{3,4})$")


class _NoRedirect(HTTPRedirectHandler):
    """Do not forward the configured key to another host."""

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        """Reject every API redirect."""
        return


OPENER = build_opener(_NoRedirect)


class QwenImageError(RuntimeError):
    """An error safe to return to an AstrBot conversation."""


def _valid_https_url(url: str) -> bool:
    try:
        parsed = urlsplit(url)
    except ValueError:
        return False
    return bool(
        parsed.scheme == "https"
        and parsed.netloc
        and not parsed.username
        and not parsed.password
    )


class QwenImageClient:
    """Submit one image or query an existing image task."""

    def __init__(self, api_key: str) -> None:
        token = api_key.strip()
        if (
            not token
            or token.lower().startswith("bearer ")
            or token.startswith("platform-")
        ):
            raise QwenImageError(
                "Set an Ace Data Cloud generation API key in plugin settings."
            )
        self._api_key = token

    def _post(self, path: str, payload: dict[str, Any]) -> tuple[dict[str, Any], str]:
        request = Request(
            API_BASE + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + self._api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "AceDataCloudAstrBot/0.1.0",
            },
            method="POST",
        )
        try:
            with OPENER.open(request, timeout=90) as response:
                body = json.load(response)
                trace_id = response.headers.get(
                    "x-trace-id", ""
                ) or response.headers.get("x-request-id", "")
        except HTTPError as exc:
            raise QwenImageError(
                f"Ace Data Cloud returned HTTP {exc.code}. Check service access and request history."
            ) from None
        except (URLError, TimeoutError, OSError):
            raise QwenImageError(
                "The API connection failed. Check request history before submitting again."
            ) from None
        except (ValueError, UnicodeError):
            raise QwenImageError(
                "The API returned invalid JSON. Check request history before retrying."
            ) from None
        if not isinstance(body, dict):
            raise QwenImageError("The API returned an unexpected response format.")
        return body, str(body.get("trace_id") or trace_id)

    async def submit(
        self,
        prompt: str,
        model: str = "qwen-image-3.0",
        size: str = "1024*1024",
        image_url: str = "",
        watermark: bool = False,
    ) -> dict[str, Any]:
        """Submit one asynchronous generation or edit, without paid retries."""
        prompt = prompt.strip()
        if not prompt or len(prompt) > 4000:
            raise QwenImageError("Provide an image prompt of 1–4000 characters.")
        if model not in MODELS:
            raise QwenImageError("Choose qwen-image-3.0 or qwen-image-3.0-pro.")
        match = SIZE_PATTERN.fullmatch(size)
        if not match or any(not 256 <= int(value) <= 4096 for value in match.groups()):
            raise QwenImageError("Size must be WIDTH*HEIGHT, 256–4096 per side.")
        if image_url and not _valid_https_url(image_url):
            raise QwenImageError("Provide an authorized HTTPS reference image URL.")
        if not isinstance(watermark, bool):
            raise QwenImageError("Watermark must be true or false.")
        payload: dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "n": 1,
            "size": size,
            "watermark": watermark,
            "async": True,
        }
        if image_url:
            payload["image_urls"] = [image_url]
        body, trace_id = await asyncio.to_thread(
            self._post, "/qwen-image/images", payload
        )
        if body.get("success") is False or body.get("error"):
            raise QwenImageError(
                "Image submission was rejected. Check request history before trying again."
            )
        task_id = body.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            raise QwenImageError(
                "No task ID was returned. Check request history before submitting again."
            )
        return {
            "status": "submitted",
            "task_id": task_id,
            "trace_id": trace_id,
            "next_step": "Query this same task ID; do not submit another image while it is pending.",
        }

    async def query(self, task_id: str) -> dict[str, Any]:
        """Return a final image URL and public usage only after task completion."""
        task_id = task_id.strip()
        if not task_id or len(task_id) > 128:
            raise QwenImageError("Pass the exact task ID from Qwen Image submission.")
        body, trace_id = await asyncio.to_thread(
            self._post,
            "/qwen-image/tasks",
            {"id": task_id, "action": "retrieve"},
        )
        if body.get("success") is False or body.get("error"):
            raise QwenImageError("Task lookup failed. Check request history.")
        response = body.get("response")
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except ValueError:
                response = None
        if not isinstance(response, dict):
            response = {}
        trace_id = str(response.get("trace_id") or trace_id)
        if response.get("success") is False or response.get("error"):
            return {
                "task_id": task_id,
                "trace_id": trace_id,
                "status": "failed",
                "success": False,
                "image_urls": [],
            }
        if (
            not response
            or ("finished_at" in body and body["finished_at"] is None)
            or response.get("success") is not True
        ):
            return {
                "task_id": task_id,
                "trace_id": trace_id,
                "status": "pending",
                "success": False,
                "image_urls": [],
            }
        items = response.get("data")
        urls = (
            [
                item["image_url"]
                for item in items
                if isinstance(item, dict)
                and isinstance(item.get("image_url"), str)
                and _valid_https_url(item["image_url"])
            ]
            if isinstance(items, list)
            else []
        )
        cost = response.get("cost")
        public_cost = (
            {
                key: cost[key]
                for key in ("amount", "list_amount", "currency")
                if key in cost
            }
            if isinstance(cost, dict)
            else {}
        )
        return {
            "task_id": task_id,
            "trace_id": trace_id,
            "status": "succeeded" if urls else "failed",
            "success": bool(urls),
            "image_urls": urls,
            "image_count": len(urls),
            "cost": public_cost,
        }
