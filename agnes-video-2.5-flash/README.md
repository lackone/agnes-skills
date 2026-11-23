# agnes-video-2.5-flash

Agnes Video 2.5 Flash 轻量异步视频生成：文生视频、首尾帧、图片/音频参考，固定 720P。

- 模型 ID：`agnes-video-2.5-flash`
- 创建：`POST /v1/videos`；轮询：`GET /agnesapi?model_name=agnes-video-2.5-flash`
- 时长 4–12 秒，默认 `12` 秒；图片 ≤5、音频 ≤3；**不支持参考视频**
- 默认参数：`720P`、`16:9`、`12` 秒；先回 URL，后台异步下载成片

## 运行

```bash
python examples/text-to-video.py "海边栈道上白鹭收翅落在栏杆，海浪拍岸，固定长镜头，清晨薄雾"
python examples/keyframe-video.py "https://example.com/first.png" "https://example.com/last.png" "人物回身整理衣袖，缓步走到廊下，镜头缓慢推进" "12"
python examples/image-reference.py "C:/work/character.png" "以 <Picture 1> 造型为准，在春日庭院折下一枝柳条，近景跟随" "16:9"
python examples/audio-reference.py "C:/work/bgm.mp3" "跟随 <Audio 1> 的节奏安排镜头长短，傍晚河岸步道行人经过" "16:9"

# 批量并发：JSON 数组请求，先回 URL 再后台下载
python examples/batch-videos.py --request jobs.json
```

参数均为可选位置参数，缺省走内置演示；`-h/--help` 查看参数说明。

环境变量 `AGNES_API_KEY`、`AGNES_BASE_URL` 可在 `.env` 或进程环境中配置（模板见套件根目录 `.env.example`；单独拷贝时直接设置环境变量即可）。详细参数与音频参考边界见 [MODULE.md](MODULE.md)。
