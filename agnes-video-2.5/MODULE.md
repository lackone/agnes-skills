---
name: agnes-video-2.5
description: Agnes Video 2.5 异步视频生成，支持文生视频、首尾帧控制、图片/音频/视频参考。触发词：视频生成、文生视频、图生视频、首尾帧、参考视频、音频参考、镜头运镜、720P、1080P、2K。
---

# Agnes Video 2.5

模型 ID：`agnes-video-2.5`。异步任务接口：先 `POST /v1/videos` 创建任务，再用 `video_id` 轮询 `GET /agnesapi` 取成片。支持文生视频、首尾帧控制和多模态参考（图片、音频、视频）。

## 端点与认证

- 创建：`POST /v1/videos`
- 查询：`GET /agnesapi?video_id=<VIDEO_ID>&model_name=agnes-video-2.5`
- 认证：`Authorization: Bearer <AGNES_API_KEY>`
- 配置：环境变量或 `.env` 中的 `AGNES_API_KEY`、`AGNES_BASE_URL`，默认 `https://apihub.agnes-ai.com/v1`。
- 运行环境：Python 3.10+，仅用标准库、无第三方依赖；脚本与共享模块同目录，`python examples/<脚本>.py` 直接运行。

## 公共请求字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `model` | string | 是 | 固定 `agnes-video-2.5` |
| `prompt` | string | 是 | 内容描述；参考模式可用 `<Picture N>`、`<Audio N>`、`<Video N>` 指代素材 |
| `mode` | string | 是 | `text` / `keyframe` / `reference` |
| `seconds` | string | 否 | 时长字符串 `"4"`–`"12"`，默认 `"5"` |
| `size` | string | 否 | `720P` / `1080P` / `1K` / `2K`；技能默认 `720P` |
| `aspect_ratio` | string | 否 | 默认 `16:9`；`21:9 16:9 4:3 1:1 3:4 9:16` |
| `seed` | integer | 否 | 随机种子 |
| `n` | integer | 否 | 当前仅支持 `1` |

## 模式专用字段

| 字段 | 适用模式 | 说明 |
|---|---|---|
| `first_frame` | `keyframe` | 首帧图片 URL，与 `last_frame` 至少一个 |
| `last_frame` | `keyframe` | 尾帧图片 URL |
| `images` | `reference` | 参考图片数组，最多 8 张 |
| `audios` | `reference` | 参考音频数组，最多 3 段 |
| `videos` | `reference` | 参考视频对象数组，最多 1 个 |

- `text`：不允许任何媒体字段。
- `keyframe`：只允许 `first_frame` / `last_frame`。
- `reference`：图片、音频、视频至少一类非空；不允许首尾帧。
- 参考视频对象：`{"url": "...", "start_seconds": 0, "require_audio": false}`；`url` 必须是可公开访问的视频地址。

## 参考媒体限制

- 图片：最多 8 张，单张 <15 MB，单次总大小 <50 MB，宽高 256–5760 像素。
- 视频：最多 1 个，时长 2–12 秒，<50 MB，帧率 24–60 FPS。
- 音频：最多 3 段，单段时长 2–12 秒，单段 <15 MB，单次总大小 <64 MB。
- 单次请求参考媒体总数不超过 12 个。

## 输入素材与 Data URI 口径

- 官方契约：所有媒体 URL 必须可被 Agnes 服务公开访问，不要用需要登录、内网地址或临期链接。
- 本地图片/音频由 `examples/media_input.py` 读成 Data URI 内联提交，这是实测可用的回退方式，并非文档保证；若返回 `valid supported media` 一类 400，改回公共 HTTPS URL。
- 音频格式被拒时先转 mp3 再提交。
- 参考视频仅接受 URL 对象，不做本地 Data URI 内联。

## 音频参考的边界（重要）

音频参考用于**节奏、氛围、动作节拍、镜头剪辑和环境声音感**；它**不提供音色克隆、口音迁移、台词配音或口型对齐**。成片人物说什么由 `prompt` 文本决定；不要在提示词里承诺“复刻参考音频的嗓音”。需要特定台词时，直接在提示词中描述说话内容与口型动作。

## 提交与轮询

1. 创建任务后保存响应中的 `video_id`（`id` / `task_id` 与它标识同一任务）。
2. 所有模式推荐带 `model_name` 查询；纯 `video_id` 查询仅适用于 `mode: "text"`。
3. 每隔 1–2 秒轮询一次，直到 `status` 为 `completed` 或 `failed`。
4. 只有 `completed` 时顶层 `url` 才是可交付视频地址；`internal_status` / `internal_progress` 是内部字段，以 `status` / `progress` 为准。

## 提示词规范

先把诉求整理成完整描述再提交：只保留本次请求相关的细节，不擅自添加转场、台词、音效或戏剧性变化；创意描述与 `size`、`seconds`、`aspect_ratio` 等参数分离。

按以下顺序组织描述：

1. **主体与场景**：人物或物体是谁、处于什么环境、什么时间。
2. **动作与变化**：主体如何移动，环境随时间如何变化。
3. **镜头语言**：推、拉、摇、移、跟拍、固定镜头，以及景别选择。
4. **视觉风格**：光线、色彩、材质、写实程度与整体氛围。
5. **声音与节奏**：需要时写明环境声、动作声，或引用音频素材。
6. **一致性要求**：必须保持不变的主体外观、产品细节或构图。

### 去 AI 味与一致性

- 动作与过渡自然：衣物、头发随运动真实摆动；镜头运动平稳且有依据，不为动而动。
- 避免均匀打光、贴片式假背景与塑料质感；材质、光影与环境接触关系写具体。
- 主体外观、产品细节与构图在整段时长内保持连贯，不中途漂移。

### 参考模式占位符

- `<Picture N>`、`<Audio N>`、`<Video N>` 在各自素材数组中从 1 开始编号；例如 `images` 数组第二张在提示词中写 `<Picture 2>`。
- 上传素材后要在提示词里说明用途，例如“以 `<Picture 1>` 为角色参考，跟随 `<Audio 1>` 的节奏”；只传素材、不解释用途，结果更难控制。
- 首尾帧模式：把首尾帧作为起止端点，描述两帧之间的动作与过渡，不要求成片全程复刻某一帧画面；补充起止姿态、动作过渡与镜头衔接要求。

### 分模式提示词示例

- **text 文生视频**：描述一个连贯场景及其运动，不堆砌多个无关情节。
  > 夜晚森林里，三只猫组成微型乐队向前行进，镜头平稳后退，月光穿过树叶，伴随自然脚步声与乐器声。
- **keyframe 首尾帧**：围绕两帧之间的自然过渡组织描述。
  > 人物从首帧姿态自然转身走向窗边，衣物和头发运动真实，镜头缓慢推进，平滑过渡到尾帧构图。
- **reference 图片参考**：点名参考图角色，再写画面动作与保持项。
  > 以 `<Picture 1>` 的角色与美术风格为参考，角色在花田中自然奔跑，保持外观一致，低机位跟拍。
- **reference 图片 + 音频**：分别说明视觉主体与音频承担的节奏作用。
  > 以 `<Picture 1>` 为视觉主体，跟随 `<Audio 1>` 的节奏设计动作和镜头切换，保持自然连贯。
- **reference 视频参考（仅标准版）**：沿用参考视频的动作与时序，替换目标场景。
  > 参考 `<Video 1>` 的主体动作和镜头节奏，把场景换成月光下的卧室，同时保持时序连贯。

## 示例脚本（`examples/`）

| 脚本 | 用途 | 参数 |
|---|---|---|
| `text-to-video.py` | 文生视频（只回 URL） | `[提示词] [时长] [尺寸] [画幅]` |
| `keyframe-video.py` | 首尾帧控制（只回 URL） | `[首帧] [尾帧] [提示词] [时长] [尺寸] [画幅]` |
| `image-reference.py` | 图片参考（只回 URL） | `[图片1,图片2,...] [提示词] [时长] [尺寸] [画幅]` |
| `audio-reference.py` | 音频参考（只回 URL） | `[音频1,音频2,...] [提示词] [时长] [尺寸] [画幅]` |
| `video-reference.py` | 视频参考（只回 URL） | `[参考视频URL] [提示词] [时长] [尺寸] [画幅] [起始秒数]` |
| `query-video.py` | 查询已有任务（只回 URL，不落盘） | `<video_id>` |
| `batch-videos.py` | 批量并发生成（只回 URL） | `--request <json|-> [--concurrency N]` |
| `download.py` | 独立下载进程（调度方后台拉起） | `<url> <out_dir> [index]` |

## 默认参数与交付顺序

- 用户未指定时：`720P`、比例 `16:9`、时长 `5` 秒；用户显式给出的时长 / 尺寸 / 比例以用户输入为准。
- **【强制 · 立即回 URL】** 生成类脚本（文生、首尾帧、各类参考）一返回成片 URL，必须立刻把 URL（及可直接渲染的外链视频）发到对话框展示；**禁止**等下载完成、等本地落盘后再一起回复。脚本不在进程内下载，由调度方另起独立 `download.py` 后台进程落盘，不阻塞回复；本地路径在落盘后再补报，下载失败单独提示、不影响已展示的 URL。`query-video.py` 仅查询状态，只回 URL、不落盘。

## 批量生成与本地下载

- `batch-videos.py` 读取 JSON 数组（每项含 `prompt`/`seconds`/`size`/`aspect_ratio` 及可选 `images`/`audios`/`videos`），线程池并发提交并轮询，默认最多 4 个并发，`--concurrency` 可覆盖；脚本不在进程内下载，逐条进度写 stderr，stdout 只输出一份汇总 JSON `{"ok": true, "results": [...]}`。
- 落盘由调度方逐条另起独立 `download.py <url> output/batch-videos <index>` 后台进程完成，与生成进程解耦；下载逻辑复用 `media_download.py`，流式写入，单文件默认上限 512 MiB，瞬态错误有限重试，扩展名取 Content-Type，回退到 URL 后缀。

## 错误处理与重试

- 可重试瞬态条件：网络/DNS/超时抖动，以及 HTTP 408、429、500、502、503、504；由 `examples/http_retry.py` 有限次重试（创建默认 3 次，轮询每轮 2 次）。
- 退避优先读取响应头 `Retry-After`（上限 60 秒），否则指数退避（上限 30 秒）；429 在同一进程内跨线程共享冷却窗口。
- 提交阶段：不可重试的 400/401/403/404 直接抛出并退出；5xx 重试仍可能产生重复任务并计费，重试后请核对任务清单。
- 轮询阶段：瞬态 HTTP 错误与网络抖动跳过本轮、下一轮继续；4xx 等不可重试错误立即终止轮询。
- 下载阶段：瞬态状态码按退避重试，4xx 不重试；批量任务单条失败被隔离，不影响其他任务。

## 常见问题

- `mode` 与媒体字段不匹配、或 `reference` 无任何素材，返回 400。
- 不要传 `video_url` / `video_path` / `video_reference`；参考视频用 `videos[].url`。
- 不要传 `width` / `height` / `fps` / `num_frames` / `quality` / `num_inference_steps`。
- `size` 只能用档位名，不能写像素尺寸；`aspect_ratio` 不能是 `auto`。
- 429 使用指数退避并降低轮询频率；500 稍后重试。

## 官方文档

- [Agnes Video 2.5](https://www.agnes-ai.com/zh-Hans/docs/agnes-video-25)
