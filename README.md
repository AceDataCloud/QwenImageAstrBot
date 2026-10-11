# Qwen Image for AstrBot

Generate or edit one Qwen Image 3 image in an AstrBot conversation through your own Ace Data Cloud account. `qwen_image_generate` submits one job, and `qwen_image_get_task` retrieves the same task until its final image is ready.

[简体中文指南](readme/README_zh_Hans.md) · [Qwen Image service](https://platform.acedata.cloud/services/qwen-image) · [Current prices](https://platform.acedata.cloud/models)

## Find and install

In AstrBot WebUI, open **Extensions → Plugins → AstrBot Plugin Market** and search **Qwen Image**. Confirm the card says **Qwen Image by Ace Data Cloud**, the author is **acedatacloud**, and the logo matches the [Qwen Image service icon](https://cdn.acedata.cloud/eff9c34a52.png). Install it, then check **Installed** for load errors.

The official AstrBot Cloud listing has not yet been published. After the source release is merged, **Installed → Install (+) → Install from URL** with `https://github.com/AceDataCloud/QwenImageAstrBot` can preview it. A URL installation does not prove market publication or installation.

## Configure your key

In [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications), copy a generation API key from your General application or create a key that permits both `/qwen-image/images` and `/qwen-image/tasks`. Check current pricing and your balance before submitting. Paste the key into the plugin's **Ace Data Cloud generation API key with Qwen Image access** setting. Do not add `Bearer ` or use a `platform-...` management token. AstrBot masks the field in WebUI but stores the original value in its data directory, which should be protected.

Select a chat model that supports tool calling. Allow both Qwen Image tools in the conversation's profile and persona.

## Generate once, then query

Ask the bot:

> Use `qwen_image_generate` once to create a studio product photo of a ceramic vase on a neutral background. Use `qwen-image-3.0`, size `1024*1024`, and show me the task ID.

The tool sends one asynchronous `POST /qwen-image/images` request with `n: 1` and returns `status: submitted` with a task ID. That is not a finished image. Keep the ID and ask:

> Use `qwen_image_get_task` with the exact task ID `<task_id>`. Tell me its status and final image URL. Do not generate another image.

If pending, query the same ID later. Only `status: succeeded`, `success: true`, and a final HTTPS image URL indicate completion. The plugin never retries a paid submission automatically.

To edit an image you own or may process, include its public HTTPS URL as `image_url` and describe the desired change in `prompt`. Choose `qwen-image-3.0` or `qwen-image-3.0-pro`; `size` uses `WIDTH*HEIGHT`, such as `1024*1536`. `watermark` defaults to false. This first version handles one output image and at most one reference image; batch output, multiple reference images, and advanced prompt controls are outside its scope.

## Verify and troubleshoot

In Ace Data Cloud usage, match a returned trace ID when available. The finished task may also return public `cost` amounts in Credits; verify the live usage row before treating an estimate as a charge. A task lookup reads an existing job and does not submit another generation.

| Symptom | Check |
| --- | --- |
| Plugin fails to load | AstrBot version, **Failed to Load Plugins**, and **Data & Logs → Logs**. |
| Tools are missing | Plugin enabled, active profile and persona allow both tools, chat model supports tool calling. |
| HTTP 401/403 | Key type, both allowed API paths, and account access. |
| Network error after submission | Inspect request history before generating again; a timeout may already have created a paid task. |
| Pending task | Query the same task ID later. |
| Failed task | Use the task or trace ID to inspect request history. |

The key goes only to `https://api.acedata.cloud`; redirects are rejected. The plugin exposes final image URLs and public cost fields to the model, without raw provider data. It uses Python's standard library and needs no runtime package installation.

## Verified local run and brand asset

On official AstrBot `v4.28.2`, an isolated editable installation registered both tools. ChatUI submitted one `qwen-image-3.0` image at `1024*1024` and later queried the same task ID through `qwen_image_get_task` without another generation. An initial task lookup hit a transient API connection error; repeating only the read-only lookup returned terminal success. The final PNG responded HTTP 200, `image/png`, and decoded at 1024×1024. The exact generation trace matched a successful `/qwen-image/images` usage row with 0.283834 Credits deducted; the completed task returned 0.315371 Credits as its list amount. See the [sanitized evidence](tests/e2e-results.json). This is a local editable installation; official Cloud review, market installation, and a first call from a market installation remain open.

`logo.png` is the unmodified 128×128 [current Qwen Image service icon](https://cdn.acedata.cloud/eff9c34a52.png), SHA-256 `75759f1b8ea00704cf425489363db1d8ff1c9174e28857008e9e75298e91d5f4`.
