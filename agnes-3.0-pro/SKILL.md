---
name: agnes-3.0-pro
description: Agnes 3.0 Pro 长上下文推理模型，面向智能体任务、专业文档分析、科学编码与长上下文整合。触发词：pro、3.0 pro、长上下文、推理、文档分析、编码、对话、图像理解。
---

# Agnes 3.0 Pro

模型 ID：`agnes-3.0-pro`。已正式上线的 Pro 模型，聚焦真实工作场景的多步骤任务、专业文档理解、科学编码和长上下文分析；支持文本与图像 URL 输入，输出文本，带推理能力。

## 端点与认证

- Chat Completions：`POST /v1/chat/completions`
- Responses：`POST /v1/responses`
- Messages（Anthropic 兼容）：`POST /v1/messages`
- 认证：`Authorization: Bearer <AGNES_API_KEY>`；Messages 端点使用 `x-api-key` 与 `anthropic-version: 2023-06-01`。
- 配置：环境变量或 `.env` 中的 `AGNES_API_KEY`、`AGNES_BASE_URL`，默认 `https://apihub.agnes-ai.com/v1`。
- 运行环境：Python 3.10+，仅用标准库、无第三方依赖；脚本与共享模块同目录，`python examples/<脚本>.py` 直接运行。

## Chat Completions 请求字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `model` | string | 是 | 固定 `agnes-3.0-pro` |
| `messages` | array | 是 | `system` / `user` / `assistant` 消息数组 |
| `messages[].content` | string / array | 是 | 纯文本，或含 `text`、`image_url` 的内容块数组 |
| `temperature` | number | 否 | 越低越确定 |
| `top_p` | number | 否 | 核采样 |
| `max_tokens` | integer | 否 | 最大输出 Token |
| `stream` | boolean | 否 | 流式输出 |
| `tools` | array | 否 | 函数调用工具定义 |
| `tool_choice` | string / object | 否 | 工具选择控制 |
| `chat_template_kwargs` | object | 否 | OpenAI 兼容扩展 |
| `thinking` | object | 否 | Anthropic 兼容 Thinking（`type`、`budget_tokens`） |

## 图像输入

`messages[].content` 中用 `{"type": "image_url", "image_url": {"url": "..."}}` 传入公开可访问图像 URL。

## Responses API

使用 `input` 代替 `messages`：`model`、`input`（字符串或结构化数组）、`max_output_tokens`。从 `output[].type == "message"` 且 `content[].type == "output_text"` 的块读取正文；`status` 为 `incomplete` 时加大 `max_output_tokens` 重试。

## 示例脚本（`examples/`）

| 脚本 | 用途 | 参数 |
|---|---|---|
| `basic-chat.py` | 基础对话 | `[用户问题]` |
| `image-understanding.py` | 图像理解 | `[图片URL] [问题]` |
| `responses-api.py` | Responses API 调用 | `[输入] [max_output_tokens]` |
| `thinking-mode.py` | Thinking 模式对话 | `[问题] [budget_tokens]` |

## 限制

- 上下文长度 1M Token；最大输出 256K Token。
- 输入模态：文本、图像；输出模态：文本；带推理。
- 付费模型，按缓存命中、输入、输出 Token 计费；可用性与限额以账户权限为准。

## 错误处理与重试

- 网络/超时抖动与 HTTP 408、429、500、502、503、504 由 `examples/http_retry.py` 有限次重试；退避优先读取 `Retry-After`，否则指数退避，429 跨线程共享冷却。
- 400/401/403/404 等不可重试错误直接抛出，不重试。

## 官方文档

- [Agnes 3.0 Pro](https://www.agnes-ai.com/zh-Hans/docs/agnes-30-pro)
