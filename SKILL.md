---
name: agnes-skills
description: |
Agnes AI 模型全能力套件 Skill。
包含对话/推理模型、图像生成、视频生成五类能力。
子 Skill 列表：
- agnes-3.0-flash（Agent 编程、工具编排、Thinking）
- agnes-3.0-pro（长上下文推理、专业文档分析、编码）
- agnes-image-2.5-flash（文生图、图生图、多图合成）
- agnes-video-2.5（文生视频、首尾帧、图片/音频/视频参考）
- agnes-video-2.5-flash（轻量视频生成，固定 720P）
触发词：agnes、聊天、对话、推理、工具调用、thinking、生图、图像生成、图生图、视频生成、文生视频、首尾帧、图片参考、音频参考。
---

# agnes-skills

> **部署方式：** 五个子目录各自独立，可整库安装，也可只复制需要的那个目录；每个子 Skill 自带 `SKILL.md` 与 `examples/*.py`（含 `load_env.py`），跨目录之间没有运行时依赖。全部脚本只用 Python 3.10+ 标准库，无第三方依赖，不需要虚拟环境或 `pip install`。

## 概述

| 子 Skill | 模型 ID | 核心能力 | 主要端点 |
| --- | --- | --- | --- |
| `agnes-3.0-flash` | `agnes-3.0-flash` | Agent 编程、工具编排、图像理解、Thinking | `/v1/chat/completions`、`/v1/responses`、`/v1/messages` |
| `agnes-3.0-pro` | `agnes-3.0-pro` | 长上下文推理、专业文档分析、编码 | 同上 |
| `agnes-image-2.5-flash` | `agnes-image-2.5-flash` | 文生图、图生图、多图合成 | `/v1/images/generations` |
| `agnes-video-2.5` | `agnes-video-2.5` | 文生视频、首尾帧、图片/音频/视频参考 | `/v1/videos` |
| `agnes-video-2.5-flash` | `agnes-video-2.5-flash` | 轻量视频生成、图片/音频参考 | `/v1/videos` |

## 默认路由与默认参数

用户未明确指定模型或参数时，按下表选择；用户显式给出的模型、尺寸、比例、时长等以用户输入为准。

| 场景 | 默认模型 | 默认参数 |
| --- | --- | --- |
| 文本对话 / 推理 / 工具调用 | `agnes-3.0-flash` | — |
| 生图（文生图 / 图生图 / 多图合成） | `agnes-image-2.5-flash` | 比例 `16:9`，档位 `2K` |
| 生视频（文生视频 / 首尾帧 / 图片/音频参考） | `agnes-video-2.5-flash` | 比例 `16:9`，`720P`，时长 `12` 秒 |

> 标准版 `agnes-video-2.5`、`agnes-3.0-pro` 仅在用户明确要求更高规格、长上下文推理或视频参考时选用。

## 交付顺序：先 URL，后本地文件

- 接口返回结果 URL 后，**先把 URL 发到对话框展示**，不要等待下载完成。
- 图片 / 视频的本地下载放在后台线程异步进行，**不阻塞** URL 交付与回复。
- 下载完成后，再把保存好的本地路径（或文件）发到对话框展示；下载失败单独提示，不影响已展示的 URL。
- 批量任务同一口径：任一任务完成即先回 URL，后台并发下载，下完一条展示一条；`--no-download` 只返回 URL 不落盘。

## 提示词准备

提交生成请求前，先按对应子技能的提示词规范把用户诉求整理成完整 `prompt`，不把模糊原话直接透传给接口：

- **保留明确意图**：用户给出的主体、人物、动作、服装、道具、场景、风格、画幅与约束原样保留；不擅自添加未要求的主体、叙事、镜头处理或特效。
- **缺省补全细节**：在原意之上补场景、光照、材质、构图、镜头与可见细节，使描述自然成句，不堆关键词。
- **成稿优先**：用户直接给了完整文案、或要求按原文时，原样保留，不二次改写。
- **文案与参数分离**：创意描述只进 `prompt`；`size`、`ratio`/`aspect_ratio`、`seconds` 等走各自 JSON 字段，不混写进文案。

## 快速开始

示例脚本放在各子 Skill 的 `examples/` 目录，只用 Python 3.10+ 标准库；可在命令行覆盖输入，不带参数时运行内置演示。单结果脚本参数均为可选位置参数（带默认值），批量脚本使用命名选项；所有脚本均可加 `-h/--help` 查看参数说明。

```bash
# 基础对话
python agnes-3.0-flash/examples/basic-chat.py "用通俗语言解释缓存击穿并给出防范思路"

# 文生图
python agnes-image-2.5-flash/examples/text-to-image.py "江南古镇清晨，石桥河面，炊烟升起" "2K" "16:9"

# 文生视频（异步任务，提交后轮询）
python agnes-video-2.5-flash/examples/text-to-video.py "海边栈道上白鹭收翅落在栏杆，清晨薄雾"
```

API Key 从环境变量或 `.env` 自动加载，无需手动 export；配置方式见 [README.md](./README.md)。

## 素材输入：Data URI 策略

套件**不包含对象存储/S3 上传步骤**：

- 图像生成端点官方接受公共 URL 或 Data URI 输入。
- 视频参考素材官方契约为公开 HTTPS URL；本地图片/音频转 Data URI 内联是实测可用的回退方式，并非文档保证；被 400 拒绝时改回公共 URL。
- 参考视频（仅标准版）只接受 URL 对象，不做内联。

详见各视频子 Skill 的 `SKILL.md`。

## 各子 Skill 文档

- [agnes-3.0-flash](./agnes-3.0-flash/SKILL.md)
- [agnes-3.0-pro](./agnes-3.0-pro/SKILL.md)
- [agnes-image-2.5-flash](./agnes-image-2.5-flash/SKILL.md)
- [agnes-video-2.5](./agnes-video-2.5/SKILL.md)
- [agnes-video-2.5-flash](./agnes-video-2.5-flash/SKILL.md)

## 文件结构

```
agnes-skills/
├── SKILL.md                     # 本文件（套件主文档）
├── README.md                    # 安装与使用说明
├── requirements.txt             # 纯标准库占位，无第三方依赖
├── .env.example                 # API Key 模板（复制为 .env）
├── .gitignore
├── agnes-3.0-flash/
│   ├── SKILL.md
│   ├── README.md
│   └── examples/
├── agnes-3.0-pro/
│   ├── SKILL.md
│   ├── README.md
│   └── examples/
├── agnes-image-2.5-flash/
│   ├── SKILL.md
│   ├── README.md
│   └── examples/
├── agnes-video-2.5/
│   ├── SKILL.md
│   ├── README.md
│   └── examples/
└── agnes-video-2.5-flash/
    ├── SKILL.md
    ├── README.md
    └── examples/
```
