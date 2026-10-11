"""Qwen Image tools for AstrBot through Ace Data Cloud."""

from __future__ import annotations

import json

from astrbot.api import AstrBotConfig
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star

from .client import QwenImageClient, QwenImageError


class QwenImagePlugin(Star):
    """Expose one image submission and one existing-task lookup tool."""

    def __init__(self, context: Context, config: AstrBotConfig) -> None:
        super().__init__(context)
        self.config = config

    @filter.llm_tool(name="qwen_image_generate")
    async def qwen_image_generate(
        self,
        event: AstrMessageEvent,
        prompt: str,
        model: str = "qwen-image-3.0",
        size: str = "1024*1024",
        image_url: str = "",
        watermark: bool = False,
    ) -> str:
        """Submit one billable image generation or edit job.

        Args:
            prompt(string): Description of the image or requested edit.
            model(string): qwen-image-3.0 or qwen-image-3.0-pro.
            size(string): WIDTH*HEIGHT such as 1024*1024.
            image_url(string): Optional authorized HTTPS image to edit.
            watermark(boolean): Whether to add a watermark.

        Returns:
            JSON submission status and task ID, never a finished-image claim.
        """
        try:
            result = await QwenImageClient(self.config.get("api_key", "")).submit(
                prompt, model, size, image_url, watermark
            )
        except QwenImageError as exc:
            result = {"status": "error", "message": str(exc)}
        return json.dumps(result, ensure_ascii=False)

    @filter.llm_tool(name="qwen_image_get_task")
    async def qwen_image_get_task(self, event: AstrMessageEvent, task_id: str) -> str:
        """Query a prior Qwen Image task ID without another generation.

        Args:
            task_id(string): Exact task ID from qwen_image_generate.

        Returns:
            JSON status and final image URL only after task completion.
        """
        try:
            result = await QwenImageClient(self.config.get("api_key", "")).query(
                task_id
            )
        except QwenImageError as exc:
            result = {"status": "error", "message": str(exc), "task_id": task_id}
        return json.dumps(result, ensure_ascii=False)
