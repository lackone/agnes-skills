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

每个子目录自包含 `examples/`（含 `load_env.py` 及其他本地共享模块），只保留需要的目录，放入 Agent 的 skills 目录即可。最小分发单元是整个子目录（`MODULE.md` + `README.md` + `examples/` 全部 `.py`）；不要只拷贝单个脚本，缺少同目录共享模块会导入失败。`.env`、`images/`、`videos/`、`__pycache__/` 与下载的媒体文件不随包分发。目录结构见主入口 `SKILL.md`「文件结构」。

## 运行环境

- **Python**：3.10 或更高版本；脚本只用标准库（`argparse`、`json`、`os`、`sys`、`threading`、`urllib`、`base64`、`mimetypes`、`concurrent.futures` 等）。
- **依赖**：无第三方包，不需要创建虚拟环境，也不需要 `pip install`；`requirements.txt` 仅作打包/审计占位，不声明任何外部依赖。
- **运行方式**：在对应技能目录下执行 `python examples/<脚本>.py [参数]`；脚本目录自动加入导入路径，共享模块随目录携带，子模块之间没有运行时依赖。
- **网络**：出站 HTTPS 需可达默认端点 `https://apihub.agnes-ai.com/v1`；走自建或代理网关时用 `AGNES_BASE_URL` 覆盖。
- **产物**：生成结果统一落到项目目录的 `images/`（图片）与 `videos/`（视频），没有项目目录时落到当前会话目录下的同名目录；`.env`、`images/`、`videos/`、Python 缓存与媒体文件已在 `.gitignore` 排除。

## 集成约定（供 Agent / 工作流调用）

- **参数传入**：单结果脚本用可选位置参数，批量脚本用命名选项；所有脚本支持 `-h/--help`，运行过程无交互式提问。
- **退出码**：成功退出码 0；鉴权失败、参数被拒、任务失败等情况退出码 1。
- **输出格式**：媒体脚本 stdout 只输出一个结果 JSON（成功 `{"ok": true, "url": "..."}`，失败 `{"ok": false, "error": "..."}`；批量 `{"ok": true, "results": [...]}`；下载 `{"ok": true, "path": "<绝对路径>"}`），进度与提示走 stderr，便于直接解析。脚本不内置下载，本地落盘由独立 `download.py` 后台进程完成。批量单条失败被隔离、不影响其他任务。
- **快响应与交付时序**：以后台任务方式启动脚本；先回 URL、后后台落盘的时序铁律，以及不重复读文档、不排查 Key、落盘只一份、线程池并发、纯标准库等快响应约定，统一以主入口 `SKILL.md`「交付顺序」「快响应约定」为准，本文件不重复。
- **环境隔离**：`.env` 只从环境变量或文件读取，不写入任何脚本；真实 Key 不进入日志、不打包进产物。

## 配置 API Key

复制 `.env.example` 为 `.env`，放在当前工作目录、`examples/`、技能目录或套件根目录均可；也可用 `AGNES_ENV_FILE` 直接指定环境文件。查找是固定清单、取第一个有 `AGNES_API_KEY` 的：进程环境变量 → `AGNES_ENV_FILE` → 当前工作目录 `.env` → `examples/.env` → 技能目录 `.env` → 套件根 `.env`。若脚本被复制到缓存目录运行，改设 `AGNES_ENV_FILE` 或把 Key 注入进程环境变量。

```dotenv
AGNES_API_KEY=sk-你的实际API Key
# 可选：自建/代理网关时修改
# AGNES_BASE_URL=https://apihub.agnes-ai.com/v1
```

默认端点 `https://apihub.agnes-ai.com/v1`。获取 Key：Agnes AI 平台控制台。

## 素材输入：Data URI 策略

套件不含对象存储 / S3 上传步骤，公共口径见主入口 `SKILL.md`「素材输入：Data URI 策略」。要点：本地图 / 音频可由脚本读成 Data URI 内联（实测回退、非文档保证，返回 400 `valid supported media` 时改公共 HTTPS URL）；音频被拒先转 mp3；标准版参考视频只接受 URL 对象。

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

批量任务并发与下载口径见主入口 `SKILL.md`「快响应约定」「交付顺序」；图片默认 8 路、视频 4 路，`--concurrency` 可覆盖。

## 默认路由与交付顺序

默认模型 / 参数路由、先回 URL 后后台落盘的交付时序，均以主入口 `SKILL.md`「默认路由与默认参数」「交付顺序」为准，本文件不重复。

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
