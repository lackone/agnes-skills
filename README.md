# agnes-skills

本仓库把 Agnes 开放接口按模型组织成五个内部模块，统一由 `agnes-skills` 主入口调度：主入口判断诉求类型、选定模型后，再进入对应子目录运行脚本，不需要把五个模块作为独立技能分别触发。整体部署即可调用全部能力；打包时也可只挑需要的子目录分发。

## 模型一览

| 子目录 | 模型 ID | 类型 | 主要端点 | 关键限制 |
|---|---|---|---|---|
| `agnes-3.0-flash` | `agnes-3.0-flash` | 文本 / 视觉对话、Agent 工具编排 | `/v1/chat/completions`、`/v1/responses`、`/v1/messages` | 上下文 512K，最大输出 65,536；文本 + 图像 URL 输入 |
| `agnes-3.0-pro` | `agnes-3.0-pro` | 文本 / 视觉对话、长上下文推理 | `/v1/chat/completions`、`/v1/responses`、`/v1/messages` | 上下文 1M，最大输出 256K；付费模型 |
| `agnes-image-2.5-flash` | `agnes-image-2.5-flash` | 图像生成、图生图、多图合成 | `/v1/images/generations` | 档位 1K/2K/3K/4K；比例 `1:1 3:4 4:3 16:9 9:16 2:3 3:2 21:9` |
| `agnes-video-2.5` | `agnes-video-2.5` | 视频生成（标准版） | `/v1/videos` | 720P/1080P/1K/2K；参考图 ≤8、音频 ≤3、视频 ≤1；时长 4–12 秒 |
| `agnes-video-2.5-flash` | `agnes-video-2.5-flash` | 视频生成（Flash） | `/v1/videos` | 仅 720P；参考图 ≤5、音频 ≤3；**不支持视频参考**；时长 4–12 秒 |

## 安装

### 整体安装

克隆本仓库后，Agent 可调用全部五个模型能力。

### 单独安装

每个子目录自包含 `examples/`（含 `load_env.py` 及其他本地共享模块），只保留需要的目录，放入 Agent 的 skills 目录即可。最小分发单元是整个子目录（`MODULE.md` + `README.md` + `examples/` 全部 `.py`）；不要只拷贝单个脚本，缺少同目录共享模块会导入失败。`.env`、`output/`、`__pycache__/` 与下载的媒体文件不随包分发。

```text
agnes-skills/
├── README.md
├── requirements.txt
├── .env.example
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

## 运行环境

- **Python**：3.10 或更高版本；脚本只用标准库（`argparse`、`json`、`os`、`sys`、`threading`、`urllib`、`base64`、`mimetypes`、`concurrent.futures` 等）。
- **依赖**：无第三方包，不需要创建虚拟环境，也不需要 `pip install`；`requirements.txt` 仅作打包/审计占位，不声明任何外部依赖。
- **运行方式**：在对应技能目录下执行 `python examples/<脚本>.py [参数]`；脚本目录自动加入导入路径，共享模块随目录携带，子模块之间没有运行时依赖。
- **网络**：出站 HTTPS 需可达默认端点 `https://apihub.agnes-ai.com/v1`；走自建或代理网关时用 `AGNES_BASE_URL` 覆盖。
- **产物**：生成结果下载到当前工作目录的 `output/`；`.env`、`output/`、Python 缓存与媒体文件已在 `.gitignore` 排除。

## 集成约定（供 Agent / 工作流调用）

- **参数传入**：单结果脚本用可选位置参数，批量脚本用命名选项；所有脚本支持 `-h/--help`，运行过程无交互式提问。
- **退出码**：成功退出码 0；鉴权失败、参数被拒、任务失败等情况退出码 1。
- **输出格式**：媒体脚本 stdout 只输出一个结果 JSON（成功 `{"ok": true, "url": "..."}`，失败 `{"ok": false, "error": "..."}`；批量 `{"ok": true, "results": [...]}`；下载 `{"ok": true, "path": "..."}`），进度与提示走 stderr，便于直接解析。脚本不内置下载；本地落盘由调度方另起独立 `download.py` 后台进程完成，落盘后再补报路径。批量单条失败被隔离、不影响其他任务。
- **快响应**：调度方以后台任务方式启动脚本，拿到 URL 立即先展示，不等下载与进程退出；下载由独立 `download.py` 进程保活；不重复读取子模块文档、不逐目录排查 Key（隔离执行环境读不到 `.env` 时，先从套件根 `.env` 解析并注入 `AGNES_API_KEY` 环境变量）；落盘只一份，不复制第二份；批量并发用线程池，保持纯标准库，不引入第三方异步 HTTP 依赖。
- **环境隔离**：`.env` 只从环境变量或文件读取，不写入任何脚本；真实 Key 不进入日志、不打包进产物。

## 配置 API Key

复制 `.env.example` 为 `.env`（当前工作目录、套件根目录、技能根目录或 `examples/` 目录均可，按目录逐级向上查找），填入 Key；也可用 `AGNES_ENV_FILE` 指定唯一的环境文件。隔离/沙箱执行环境若把脚本复制到缓存目录运行、导致按脚本目录找不到 `.env`，改为先读取套件根 `.env`、把 `AGNES_API_KEY` 注入进程环境变量后再启动脚本。

```dotenv
AGNES_API_KEY=sk-你的实际API Key
# 可选：自建/代理网关时修改
# AGNES_BASE_URL=https://apihub.agnes-ai.com/v1
```

默认端点 `https://apihub.agnes-ai.com/v1`。获取 Key：Agnes AI 平台控制台。

## 素材输入：Data URI 策略

套件**不包含对象存储/S3 上传步骤**。本地图片、音频在示例脚本内直接读成 Base64 Data URI 内联提交：

- **图像生成端点**：官方文档明确接受公共 URL 或 Data URI Base64 输入，本地图片可直接内联。
- **视频参考素材**：官方文档契约为「可公开访问的 HTTPS URL」。本地图片/音频转 Data URI 内联属于**实测可用的未文档化回退**，不保证后续版本持续放行；若返回 400 `valid supported media`，应改为公共 HTTPS URL 重试。音频格式不被接受时先转 mp3。
- 参考视频（仅标准版 `agnes-video-2.5`）只接受 URL 对象，不做内联。

## 运行示例

示例脚本只使用 Python 3.10+ 标准库；不带参数时跑内置演示，带参数时覆盖对应输入。单结果脚本参数均为可选位置参数（带默认值），批量脚本使用命名选项；所有脚本均可加 `-h/--help` 查看参数说明：

```bash
# 文生图
python agnes-image-2.5-flash/examples/text-to-image.py "江南古镇清晨，石桥河面，炊烟升起" "1K" "16:9"

# 基础对话
python agnes-3.0-flash/examples/basic-chat.py "用通俗语言解释缓存击穿并给出防范思路"

# 文生视频
python agnes-video-2.5-flash/examples/text-to-video.py "海边栈道上白鹭收翅落在栏杆，清晨薄雾"
```

视频为异步任务：提交后用返回的 `video_id` 轮询 `GET /agnesapi?model_name=<模型ID>`（网关去掉 `/v1` 前缀），通常需要 2–5 分钟；Flash 进度在生成中常停留在 10，完成后跳到 100。

批量任务：`batch-images.py` / `batch-videos.py` 线程池并发提交，图片默认最多 8 路、视频默认最多 4 路，可用 `--concurrency` 覆盖；脚本只回 URL 清单、不在进程内下载，落盘由调度方逐条另起独立 `download.py <url> <out_dir> [index]` 后台进程完成，与生成进程解耦。

## 默认路由与默认参数

用户未明确指定时按下列默认值选择；用户显式给出的模型、尺寸、比例、时长以用户输入为准：

| 场景 | 默认模型 | 默认参数 |
|---|---|---|
| 文本对话 / 推理 / 工具调用 | `agnes-3.0-flash` | — |
| 生图 | `agnes-image-2.5-flash` | `16:9`，`1K` |
| 生视频 | `agnes-video-2.5-flash` | `16:9`，`720P`，`12` 秒 |

## 交付顺序：先 URL，后本地文件

接口返回 URL 后先把链接发到对话框展示；单结果脚本不在进程内下载，由独立 `download.py` 后台进程落盘，不阻塞回复；下载完成后再展示保存好的本地路径。下载失败单独提示，不影响已展示的 URL。批量任务同理：脚本只回 URL 清单、不在进程内下载，落盘由调度方逐条另起独立 `download.py` 后台进程完成。

## 错误处理与重试

- 各技能 `examples/http_retry.py` 统一处理：网络/超时抖动与 HTTP 408、429、500、502、503、504 有限次重试；400/401/403/404 等不重试。
- 退避优先读 `Retry-After`（上限 60 秒），否则指数退避（上限 30 秒）；429 在进程内跨线程共享冷却。
- 视频轮询遇瞬态错误跳过本轮继续；下载复用同一套状态码分类。创建请求在 5xx 后重试可能产生重复任务并计费，重试后请核对任务清单。

## 官方文档

- [Agnes 3.0 Flash](https://www.agnes-ai.com/zh-Hans/docs/agnes-30-flash)
- [Agnes 3.0 Pro](https://www.agnes-ai.com/zh-Hans/docs/agnes-30-pro)
- [Agnes Image 2.5 Flash](https://www.agnes-ai.com/zh-Hans/docs/agnes-image-25-flash)
- [Agnes Video 2.5](https://www.agnes-ai.com/zh-Hans/docs/agnes-video-25)
- [Agnes Video 2.5 Flash](https://www.agnes-ai.com/zh-Hans/docs/agnes-video-25-flash)
