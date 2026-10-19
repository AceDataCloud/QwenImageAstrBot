# AstrBot 的 Qwen Image 插件

通过自己的 Ace Data Cloud 账号，在 AstrBot 对话中生成或编辑单张 Qwen Image 3 图片。`qwen_image_generate` 提交一次任务，`qwen_image_get_task` 用相同 ID 查询到最终结果。

这是 **Ace Data Cloud 提供的 Qwen Image 独立集成**，不是 Qwen Image 厂商或 AstrBot 团队的官方插件。请使用自己的 Ace API Key。

[English guide](../README.md) · [Qwen Image 服务](https://platform.acedata.cloud/services/qwen-image?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=qwenimageastrbot_readme_services_qwen_image) · [当前价格](https://platform.acedata.cloud/models?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=qwenimageastrbot_readme_pricing)

## 1. 查找与安装

当前上游菜单为 **插件 → 顶部插件 → 插件市场 / 已安装**；旧英文版本可能仍写 Extensions。在插件市场搜索 **Qwen Image**，核对 **Qwen Image by Ace Data Cloud**、作者 **acedatacloud** 与对应服务图标。

**2026-10-19 发布状态：尚未在官方市场公开上架。** 上面的搜索/安装是正式上架后的路径；当前不要等待不存在的卡片，请用下一段的仓库地址手动安装。

仓库安装：**插件 → 插件 → 已安装 → 安装插件（+）→ 从链接安装**，输入 `https://github.com/AceDataCloud/QwenImageAstrBot`。源码已经存在；安装后核启用和加载状态。仓库/文件安装与官方市场安装分别记账。

## 配置 Key

首次使用请先注册并登录；如果应用页还没有通用应用，点击 **初始化通用应用（Initialize General Application）**，再按下面步骤管理密钥。

到 [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=qwenimageastrbot_readme_api_key) 复制 General application 的生成 API Key，或创建同时允许 `/qwen-image/images` 和 `/qwen-image/tasks` 的 Key。提交前检查当前价格和余额。在插件设置 **Ace Data Cloud generation API key with Qwen Image access** 中粘贴 Key 本身；不要加 `Bearer `，也不要使用 `platform-...` 管理 Token。AstrBot WebUI 会遮蔽字段，但数据目录会保存原值，请保护该目录。

选择支持工具调用的聊天模型，在当前 Profile 和 Persona 中允许两个 Qwen Image 工具。

### Token 图文：复制或创建专用 Key

先[注册或登录 Ace](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=qwenimageastrbot_readme_signup)，打开 **Applications → General application**；没有通用应用时先初始化。图中 **1** 复制现有 Key，**2 Manage Keys → Create** 创建专用 Key。API 限制开启时应包含 `/qwen-image/images`、`/qwen-image/tasks`，并检查账户当前权限、余额与价格。

![Ace 应用页复制 Key 或管理 Key（已脱敏）](../_assets/tutorial/get-api-key-en.png)

专用 Key 可命名为 `AstrBot Qwen Image`；到期和限额按需设置。下图中的 `Dify tutorial` 是旧示例名称，不需要照抄。

![创建专用 API Key（共享 Ace 页面，非 AstrBot）](../_assets/tutorial/create-api-key-en.png)

两张图于 **2026-10-19** 复用核验，原拍摄日期未知，凭据/App ID/余额均已脱敏；这是共享 Ace Applications 页面，不是 AstrBot 安装或真实调用证明。[原图来源与限制](../_assets/tutorial/sources.json)。

### 在 AstrBot 填写哪里

打开 **插件 → 插件 → 已安装**，点击 **Qwen Image by Ace Data Cloud** 卡片齿轮（插件配置），在 **Ace Data Cloud generation API key with Qwen Image access**（字段 `api_key`）粘贴 Key 并保存。只填 Key 本身，不加 `Bearer `；不填到模型提供商或聊天消息。界面遮罩不加密磁盘配置，请保护 AstrBot 数据目录。此处提供准确文字路径；不以假界面代替本插件最新设置截图。

## 只生成一次，再查同一任务

向机器人发送：

> 只调用一次 `qwen_image_generate`，生成中性背景上的陶瓷花瓶产品照。模型用 `qwen-image-3.0`，尺寸 `1024*1024`，告诉我 task ID。

工具向 `POST /qwen-image/images` 提交一次异步任务，固定 `n: 1`，返回 `status: submitted` 和 task ID；此时并非最终图片。保留 ID，再问：

> 用 `qwen_image_get_task` 查询原来的 `<task_id>`，告诉我状态和最终图片 URL，不要再次生成。

若仍为 pending，稍后查询**同一 ID**。只有 `status: succeeded`、`success: true` 且返回最终 HTTPS 图片 URL 才表示完成。插件不会自动重试付费请求。

若要编辑有处理权限的图片，将其公开 HTTPS 地址传为 `image_url`，在 `prompt` 描述修改。可选 `qwen-image-3.0` 或 `qwen-image-3.0-pro`；`size` 使用 `WIDTH*HEIGHT`，如 `1024*1536`。`watermark` 默认 false。首版只处理单张输出和至多一张参考图；批量输出、多参考图和高级提示词参数暂未包含。

## 用量与排障

在 Ace Data Cloud 用量页按返回的 trace ID 匹配。已完成的任务也可能返回公开 `cost` 字段，单位 Credits；以线上用量记录为准，不把预估当成实扣。任务查询只读取已有作业，不会再提交生成。

| 现象 | 检查项 |
| --- | --- |
| 插件加载失败 | AstrBot 版本、**Failed to Load Plugins**、**Data & Logs → Logs**。 |
| 看不到工具 | 插件启用、当前 Profile/Persona 允许两个工具、聊天模型支持工具调用。 |
| HTTP 401/403 | Key 类型、两个 Allowed APIs 路径和账号权限。 |
| 提交后网络错误 | 再次生成前查请求历史；超时请求可能已创建付费任务。 |
| 任务 pending | 稍后查询同一个 task ID。 |
| 任务 failed | 按 task ID 或 trace ID 查看请求历史。 |

Key 只发送到 `https://api.acedata.cloud`，重定向会被拒绝。插件仅向模型返回最终图片链接和公开成本字段，不透出上游原始数据。运行只需 Python 标准库。

## 已验证的本地运行与图标

官方 AstrBot `v4.28.2` 的隔离实例注册了两个工具。ChatUI 用 `qwen-image-3.0` 提交一次 `1024*1024` 图片任务，并通过 `qwen_image_get_task` 查询同一 task ID，没有再次生成。首次任务查询遇到短暂连接错误；仅重试只读查询后得到终态成功。最终 PNG 为 HTTP 200、`image/png`，解码尺寸 1024×1024。生成 trace 精确匹配一条成功的 `/qwen-image/images` 用量，实扣 0.283834 Credits；完成任务返回的原价为 0.315371 Credits。详见[脱敏证据](../tests/e2e-results.json)。这仍是本地 editable 安装；Cloud 审核、官方市场安装及市场安装后的首次调用尚未完成。

`logo.png` 是未经修改的 128×128 [当前 Qwen Image 服务图标](https://cdn.acedata.cloud/eff9c34a52.png)，SHA-256 `75759f1b8ea00704cf425489363db1d8ff1c9174e28857008e9e75298e91d5f4`。
