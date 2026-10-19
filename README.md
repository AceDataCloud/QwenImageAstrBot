# Qwen Image for AstrBot

Generate or edit one Qwen Image 3 image in an AstrBot conversation through your own Ace Data Cloud account. `qwen_image_generate` submits one job, and `qwen_image_get_task` retrieves the same task until its final image is ready.

This independent **Qwen Image integration is provided by Ace Data Cloud**; it is not an official plugin from the Qwen Image publisher or the AstrBot team. Use your own Ace API key.

[简体中文指南](readme/README_zh_Hans.md) · [Qwen Image service](https://platform.acedata.cloud/services/qwen-image?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=qwenimageastrbot_readme_services_qwen_image) · [Current prices](https://platform.acedata.cloud/models?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=qwenimageastrbot_readme_pricing)

## 1. Find and install

Current upstream navigation is **Plugins → Plugins → Plugin Market / Installed**; older English versions may label the section Extensions. Search **Qwen Image** and verify **Qwen Image by Ace Data Cloud**, author **acedatacloud**, and the matching service icon.

**Publication status on 2026-10-19: not publicly listed in the official market.** The market search/install instructions above apply after publication. For the current preview, use the repository path below rather than waiting for a card that is not there.

Repository installation: **Plugins → Plugins → Installed → Install Plugin (+) → Install from URL**, with `https://github.com/AceDataCloud/QwenImageAstrBot`. Source is already available. Confirm it is enabled and loaded. A repository/file installation is a separate path from official market installation.

## Configure your key

New account? Register and sign in first. If the Applications page has no General application yet, choose **Initialize General Application**, then continue with the key steps below.

In [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=qwenimageastrbot_readme_api_key), copy a generation API key from your General application or create a key that permits both `/qwen-image/images` and `/qwen-image/tasks`. Check current pricing and your balance before submitting. Paste the key into the plugin's **Ace Data Cloud generation API key with Qwen Image access** setting. Do not add `Bearer ` or use a `platform-...` management token. AstrBot masks the field in WebUI but stores the original value in its data directory, which should be protected.

Select a chat model that supports tool calling. Allow both Qwen Image tools in the conversation's profile and persona.

### Token screenshots: copy or create a dedicated key

[Register or sign in to Ace](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=qwenimageastrbot_readme_signup), then open **Applications → General application** and initialize it if absent. Use **1** to copy the selected key, or **2 Manage Keys → Create** for a dedicated key. If Allowed APIs is enabled, include `/qwen-image/images` and `/qwen-image/tasks`; check current entitlement, balance and prices before use.

![Copy an Ace key or open Manage Keys (redacted)](_assets/tutorial/get-api-key-en.png)

Use a name such as `AstrBot Qwen Image` and set expiry/limits as needed. The screenshot’s `Dify tutorial` is an older example, not a required label.

![Create an optional dedicated API key (shared Ace page, not AstrBot)](_assets/tutorial/create-api-key-en.png)

Images were reused and checked on **2026-10-19**; original capture dates are unknown. Credentials, App ID and balance are redacted. This is the shared Ace Applications UI, not proof of AstrBot installation or a live service call. [Image sources and limits](_assets/tutorial/sources.json).

### Where to paste it in AstrBot

Open **Plugins → Plugins → Installed**, select the gear (**Plugin Configuration**) on **Qwen Image by Ace Data Cloud**, paste the key into **Ace Data Cloud generation API key with Qwen Image access** (stored field `api_key`), and save. Paste the key only, with no `Bearer ` prefix; never put it in model-provider settings or a chat prompt. UI masking does not encrypt the data-directory config. These are exact text steps; no fabricated settings image is used.

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
