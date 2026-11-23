# agnes-image-2.5-flash

Agnes Image 2.5 Flash 图像生成、图生图与多图合成。

- 模型 ID：`agnes-image-2.5-flash`
- 端点：`/v1/images/generations`
- 尺寸档位 1K/2K/3K/4K，比例 `1:1 3:4 4:3 16:9 9:16 2:3 3:2 21:9`
- 默认参数：`2K`、`16:9`；先回 URL，后台异步下载成片

## 运行

```bash
python examples/text-to-image.py "江南古镇清晨，石桥河面，白墙黑瓦间炊烟升起，水墨质感" "2K" "16:9"
python examples/image-to-image.py "C:/work/source.png" "保留姿态构图，背景换成雪后初晴的古镇茶馆，暖调胶片" "2K" "16:9"
python examples/multi-image-combine.py "https://example.com/c1.png" "https://example.com/c2.png" "两位人物同处一张茶席，竹帘背景，淡彩国风"

# 批量并发：JSON 数组请求，先回 URL 再后台下载
python examples/batch-images.py --request prompts.json
```

参数均为可选位置参数，缺省走内置演示；`-h/--help` 查看参数说明。

环境变量 `AGNES_API_KEY`、`AGNES_BASE_URL` 可在 `.env` 或进程环境中配置（模板见套件根目录 `.env.example`；单独拷贝时直接设置环境变量即可）。详细参数见 [MODULE.md](MODULE.md)。
