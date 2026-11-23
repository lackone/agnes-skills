---
name: agnes-3.0-flash
description: Agnes 3.0 Flash 文本/视觉对话模型，面向 Agent 编程、工具调用与长任务执行。触发词：agent、工具调用、tool calling、3.0、thinking、对话、聊天、图像理解。
---

# Agnes 3.0 Flash

模型 ID：`agnes-3.0-flash`，**套件默认文本对话模型**：用户未指定对话 / 推理 / 工具调用所用模型时选用本模型；`agnes-3.0-pro` 仅在用户明确要求长上下文、专业推理或编码时调用。新一代文本模型，强化 Agnes Code 任务执行、工具编排、指令与上下文遵循和可信交付；支持文本与图像 URL 输入，输出文本。

## 端点与认证

- Chat Completions：`POST /v1/chat/completions`
- Responses：`POST /v1/responses`
- Messages（Anthropic 兼容）：`POST /v1/messages`
- 认证：`Authorization: Bearer <AGNES_API_KEY>`；Messages 端点使用 `x-api-key` 与 `anthropic-version: 2023-06-01`。
- 配置：从环境变量或 `.env` 读取 `AGNES_API_KEY`、`AGNES_BASE_URL`，默认 `https://apihub.agnes-ai.com/v1`。
- 运行环境：Python 3.10+，仅用标准库、无第三方依赖；脚本与共享模块同目录，`python examples/<脚本>.py` 直接运行。

## Chat Completions 请求字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `model` | string | 是 | 固定 `agnes-3.0-flash` |
| `messages` | array | 是 | `system` / `user` / `assistant` 消息数组 |
| `messages[].content` | string / array | 是 | 纯文本，或含 `text`、`image_url` 的内容块数组 |
| `temperature` | number | 否 | 输出随机性 |
| `top_p` | number | 否 | 核采样 |
| `max_tokens` | integer | 否 | 最大输出 Token |
| `stream` | boolean | 否 | 流式输出 |
| `tools` | array | 否 | 函数调用工具定义 |
| `tool_choice` | string / object | 否 | 工具选择控制 |
| `chat_template_kwargs` | object | 否 | Thinking 等兼容扩展 |

## 图像输入

在 `messages[].content` 中用内容块传入公开可访问的图像 URL：

```json
{ "type": "image_url", "image_url": { "url": "https://example.com/image.jpg" } }
```

## 工具调用

`tools` 按 OpenAI function calling 格式定义；模型返回 `choices[].message.tool_calls` 后，在应用侧执行函数，把结果追加到 `messages` 再发下一次请求。示例脚本只演示请求与解析，不内置真实工具执行。

## Thinking 模式

OpenAI 兼容格式在 `chat_template_kwargs` 中开启：

```json
"chat_template_kwargs": { "enable_thinking": true }
```

## 示例脚本（`examples/`）

| 脚本 | 用途 | 参数 |
|---|---|---|
| `basic-chat.py` | 基础对话 | `[用户问题]` |
| `image-understanding.py` | 图像理解 | `[图片URL] [问题]` |
| `tool-calling.py` | 函数调用请求与解析 | `[用户问题]` |
| `thinking-mode.py` | Thinking 模式对话 | `[问题] [max_tokens]` |

## 限制

- 上下文窗口 512K；最大输出 65,536 Token。
- 输入模态：文本、图像 URL；输出模态：文本。
- 模型可用性、速率限制与计费以账户和 API Key 权限为准。

## 错误处理与重试

- 网络/超时抖动与 HTTP 408、429、500、502、503、504 由 `examples/http_retry.py` 有限次重试；退避优先读取 `Retry-After`，否则指数退避，429 跨线程共享冷却。
- 400/401/403/404 等不可重试错误直接抛出，不重试。

## 官方文档

- [Agnes 3.0 Flash](https://www.agnes-ai.com/zh-Hans/docs/agnes-30-flash)
