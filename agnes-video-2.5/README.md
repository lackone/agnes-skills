# agnes-video-2.5

Agnes Video 2.5 异步视频生成：文生视频、首尾帧、图片/音频/视频参考。

- 模型 ID：`agnes-video-2.5`
- 创建：`POST /v1/videos`；轮询：`GET /agnesapi?model_name=agnes-video-2.5`
- 时长 4–12 秒；尺寸 `720P / 1080P / 1K / 2K`；图片 ≤8、音频 ≤3、视频 ≤1

## 运行

```bash
python examples/text-to-video.py "竹林小径上素色长衫的人缓步前行，落叶掠过，镜头跟拍" "5" "720P" "16:9"
python examples/keyframe-video.py "https://example.com/first.png" "https://example.com/last.png" "人物由坐姿起身走到画架前，镜头平稳跟随" "5"
python examples/image-reference.py "./character.png" "以 <Picture 1> 造型服饰为准，在古镇回廊驻足看游鱼，中景横移" "5" "720P" "16:9"
python examples/audio-reference.py "./bgm.mp3" "按 <Audio 1> 的节拍与氛围安排集市摊位依次掠过的剪辑" "5" "720P" "16:9"
python examples/video-reference.py "https://example.com/clip.mp4" "沿用 <Video 1> 的动作时序与镜头衔接，换成清晨天台花园" "5"

# 单结果只回 URL；拿到 URL 后另起独立进程下载到本地
python examples/download.py "<成片URL>" "<videos 绝对路径>"

# 批量并发：JSON 数组请求，只回 URL；落盘逐条用独立 download.py
python examples/batch-videos.py --request jobs.json
python examples/download.py "<成片URL>" "<videos 绝对路径>" <序号>
```

参数均为可选位置参数，缺省走内置演示；`-h/--help` 查看参数说明。

环境变量 `AGNES_API_KEY`、`AGNES_BASE_URL` 可在 `.env` 或进程环境中配置（模板见套件根目录 `.env.example`；单独拷贝时直接设置环境变量即可）。详细参数与音频参考边界见 [MODULE.md](MODULE.md)。
