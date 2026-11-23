---
name: agnes-skills
description: "Agnes AI 全能力套件，统一入口 agnes-skills，按诉求分发到内部模块：3.0 Flash/Pro 对话推理、Image 2.5 Flash 生图、Video 2.5/2.5 Flash 生视频；五个子目录是内部模块，不需要作为独立技能分别触发。触发词：agnes、聊天、对话、推理、工具调用、thinking、生图、图像生成、图生图、多图合成、视频生成、文生视频、首尾帧、图片参考、音频参考。"
---

# agnes-skills

> **部署方式：** 打包时五个子目录各自自包含（自带 `MODULE.md` 与 `examples/*.py`，含 `load_env.py`），可整库安装，也可只复制需要的目录；运行时统一由本入口调度，跨目录之间没有运行时依赖。全部脚本只用 Python 3.10+ 标准库，无第三方依赖，不需要虚拟环境或 `pip install`。

## 调度方式（唯一入口）

- 本套件对外只有 `agnes-skills` 一个入口；下面五个目录是**内部能力模块**，不是五个需要单独触发、单独调用的技能。
- 主入口调用流程：
  1. 判断用户诉求类型：对话 / 推理 / 工具调用、生图、生视频；
  2. 按「默认路由与默认参数」表选定模型；
  3. 默认参数、端点与交付口径以本文件为准，直接运行对应脚本；仅当请求字段、比例档位或报错处理在本文件查不到时，才打开对应子目录 `MODULE.md` 核查；
  4. 运行该目录 `examples/` 下对应脚本；
  5. 结果按本文件「交付顺序」「快响应约定」与「错误处理与重试」口径返回。
- 子目录的 `README.md` / `MODULE.md` 仅供主入口调度时查阅，不直接对用户单独展示。

## 概述

| 子模块 | 模型 ID | 核心能力 | 主要端点 |
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
| 生图（文生图 / 图生图 / 多图合成） | `agnes-image-2.5-flash` | 比例 `16:9`，档位 `1K` |
| 生视频（文生视频 / 首尾帧 / 图片/音频参考） | `agnes-video-2.5-flash` | 比例 `16:9`，`720P`，时长 `12` 秒 |

> 标准版 `agnes-video-2.5`、`agnes-3.0-pro` 仅在用户明确要求更高规格、长上下文推理或视频参考时选用。

## 交付顺序：先 URL，后本地文件

- 接口返回结果 URL 后，**先把 URL 发到对话框展示**，不要等待下载完成。
- **单结果生成脚本只回 URL，不在进程内下载**；拿到 URL 后，调度方另起一个独立后台进程运行同目录 `download.py <url> <out_dir> [index]` 落盘。下载进程与生成脚本生命周期解耦——生成脚本退出不会牵连下载进程，避免内置线程被进程退出中断。
- 下载完成后，再把保存好的本地路径（或文件）发到对话框展示；下载失败单独提示，不影响已展示的 URL。
- 批量任务（`batch-images.py` / `batch-videos.py`）同样**只并发生成、逐条回 URL，不在进程内下载**；生成脚本退出不牵连下载。拿到 URL 清单后，调度方逐条另起独立后台进程运行 `download.py <url> <out_dir> [index]` 落盘。批量脚本无 `--output` / `--no-download` 参数。
- 查询类脚本（`query-video.py`）只回 URL、不落盘。

## 输出契约（供 agent 机器解析）

媒体生成 / 查询 / 下载脚本的 **stdout 只输出一个结果 JSON**，调度方直接 `json.loads(stdout)` 取结果；所有进度、`[完成]/[失败]`、轮询状态、原始响应调试信息一律写 **stderr**，不污染 stdout。

- 单结果成功：`{"ok": true, "url": "...", "video_id": "..."}`（视频带 `video_id`；Base64 直落盘为 `{"ok": true, "path": "..."}`）。
- 下载成功：`{"ok": true, "path": "...", "index": 0}`。
- 失败：`{"ok": false, "error": "..."}`，进程退出码为 1。
- 批量：`{"ok": true, "results": [{"index": 0, "ok": true, "url": "...", "video_id": "..."}, {"index": 1, "ok": false, "error": "..."}]}`，单条失败隔离在条目内，不影响其他条目。
- 解析约定：结果只从 stdout 的 JSON 取；stderr 仅作日志排查，不作为结果来源。3.0 对话类脚本产物是文本回复，不适用本契约。
- 边界：鉴权缺失、任务创建失败、轮询超时、不可重试 HTTP 错误等致命异常由公共件以非零退出码终止，原因写在 stderr，此时 stdout 可能为空；调度方结合退出码与 stderr 判断失败，不要等待 stdout JSON。

## 快响应约定（强制）

以下条目用于压缩首响时间，调度时逐条遵守，不得省略：

1. **不重复加载文档**：模型路由、默认参数、端点、交付顺序以本文件为准；不预先通读子模块 `MODULE.md`、脚本源码或共享模块源码。仅当参数/限制/报错在本文件未覆盖时，才定点查阅对应 `MODULE.md`。
2. **不排查 API Key**：`load_env` 自动从环境变量或 `.env` 读取 Key；不要逐目录找 Key、不要打印或回显 Key 内容。若在隔离/沙箱执行环境中后台脚本报「未配置 API Key」（脚本被复制到缓存目录执行，`__file__` 指向副本，按脚本目录向上查找 `.env` 落空），调度方先读取套件根 `.env`，把 `AGNES_API_KEY` 注入当前进程环境变量后再启动脚本；仍失败再按鉴权错误转达。
3. **前置探测合并、能省则省**：Python 版本、工作目录等必须确认的事项合并到一条命令完成；无必要不单独探测。
4. **脚本后台运行，结果先抛**：生成脚本按后台任务方式启动；从 stdout 的结果 JSON 取出成片 URL 即先展示给用户，**不等下载结束、不等进程退出**；下载由独立 `download.py` 后台进程完成，本地路径在其落盘后再补报。下载失败不影响已展示的 URL。
5. **落盘只一份**：脚本下载产出唯一文件，不手动复制、不改名生成第二份；需要可读文件名时在下载环节一次定名。
6. **并发用线程池，不引入异步依赖**：批量任务沿用 `ThreadPoolExecutor` 并发，默认图片最多 8 路、视频最多 4 路，`--concurrency` 可覆盖；套件保持纯标准库，不新增 aiohttp/httpx 等第三方包，也不把阻塞 urllib 包装成伪 asyncio。单任务场景同步一次请求即可，瓶颈在服务端生成，本地改协程无收益。
7. **不重复提交**：服务端生成/轮询期间不重发创建请求；瞬态错误由 `http_retry` 有限次退避重试，最终失败再如实告知。

### 执行环境已知坑（避免重复踩）

- **后台读不到 Key**：隔离/沙箱会把脚本复制到缓存目录执行，`__file__` 指向副本，`load_env` 沿脚本目录向上找 `.env` 落空；`AGNES_ENV_FILE` 指向的真实 `.env` 在后台也可能打不开（`OSError` 被静默）。兜底：启动前从套件根 `.env` 解析 `AGNES_API_KEY` 注入进程环境变量，不要回显 Key。
- **内置后台线程下载会被中断**：早期单结果脚本用 `daemon=True` 线程下载，生成脚本 `main` 返回、进程退出时守护线程被直接终止，文件落不完。现已改为生成脚本只回 URL、下载交给独立 `download.py` 进程；不要再在生成脚本内起线程下载。
- **轮询等待口径**：视频轮询固定 2 秒一轮（非累加退避）；请求失败重试才走指数退避。长等待主要来自服务端排队出片，本地无法压缩。

### 耗时边界（供判断）

- **本地可压缩**：文档加载、Key 排查、前置探测、前台阻塞等待下载、多余文件复制——按本节约定消除。
- **本地不可压缩**：服务端排队与生成耗时（出图随档位升高变慢，视频通常 2–5 分钟）、网络往返、有限次重试退避；这部分只能先回 URL、后台等待。

## 提示词准备

提交生成请求前，先按对应子技能的提示词规范把用户诉求整理成完整 `prompt`，不把模糊原话直接透传给接口：

- **保留明确意图**：用户给出的主体、人物、动作、服装、道具、场景、风格、画幅与约束原样保留；不擅自添加未要求的主体、叙事、镜头处理或特效。
- **缺省补全细节**：在原意之上补场景、光照、材质、构图、镜头与可见细节，使描述自然成句，不堆关键词。
- **成稿优先**：用户直接给了完整文案、或要求按原文时，原样保留，不二次改写。
- **文案与参数分离**：创意描述只进 `prompt`；`size`、`ratio`/`aspect_ratio`、`seconds` 等走各自 JSON 字段，不混写进文案。

## 快速开始

示例脚本放在各子模块的 `examples/` 目录，只用 Python 3.10+ 标准库；可在命令行覆盖输入，不带参数时运行内置演示。单结果脚本参数均为可选位置参数（带默认值），批量脚本使用命名选项；所有脚本均可加 `-h/--help` 查看参数说明。

```bash
# 基础对话
python agnes-3.0-flash/examples/basic-chat.py "用通俗语言解释缓存击穿并给出防范思路"

# 文生图
python agnes-image-2.5-flash/examples/text-to-image.py "江南古镇清晨，石桥河面，炊烟升起" "1K" "16:9"

# 文生视频（异步任务，提交后轮询）
python agnes-video-2.5-flash/examples/text-to-video.py "海边栈道上白鹭收翅落在栏杆，清晨薄雾"
```

API Key 从环境变量或 `.env` 自动加载，无需手动 export；配置方式见 [README.md](./README.md)。

## 素材输入：Data URI 策略

套件**不包含对象存储/S3 上传步骤**：

- 图像生成端点官方接受公共 URL 或 Data URI 输入。
- 视频参考素材官方契约为公开 HTTPS URL；本地图片/音频转 Data URI 内联是实测可用的回退方式，并非文档保证；被 400 拒绝时改回公共 URL。
- 参考视频（仅标准版）只接受 URL 对象，不做内联。

详见各视频子模块的 `MODULE.md`。

## 内部模块文档（主入口调度时查阅）

- [agnes-3.0-flash](./agnes-3.0-flash/MODULE.md)
- [agnes-3.0-pro](./agnes-3.0-pro/MODULE.md)
- [agnes-image-2.5-flash](./agnes-image-2.5-flash/MODULE.md)
- [agnes-video-2.5](./agnes-video-2.5/MODULE.md)
- [agnes-video-2.5-flash](./agnes-video-2.5-flash/MODULE.md)

## 文件结构

```
agnes-skills/
├── SKILL.md                     # 本文件（套件主文档）
├── README.md                    # 安装与使用说明
├── requirements.txt             # 纯标准库占位，无第三方依赖
├── .env.example                 # API Key 模板（复制为 .env）
├── .gitignore
├── agnes-3.0-flash/
│   ├── MODULE.md
│   ├── README.md
│   └── examples/
├── agnes-3.0-pro/
│   ├── MODULE.md
│   ├── README.md
│   └── examples/
├── agnes-image-2.5-flash/
│   ├── MODULE.md
│   ├── README.md
│   └── examples/
├── agnes-video-2.5/
│   ├── MODULE.md
│   ├── README.md
│   └── examples/
└── agnes-video-2.5-flash/
    ├── MODULE.md
    ├── README.md
    └── examples/
```
