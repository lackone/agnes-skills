#!/usr/bin/env python3
"""图片参考（固定 720P，最多 5 张）：agnes-video-2.5-flash

图片可为本地路径、公共 HTTPS URL 或 Data URI；本地文件会被读成 Data URI 内联提交。
多张图片用英文逗号分隔。

用法：python image-reference.py [图片1,图片2,...] [提示词] [画幅]
"""
import argparse
import sys

import media_download
import media_input
import video_common


def parse_args():
    parser = argparse.ArgumentParser(description="图片参考（固定 720P）：agnes-video-2.5-flash")
    parser.add_argument("sources", nargs="?", default="https://example.com/character.png", help="参考图片，多张用英文逗号分隔")
    parser.add_argument("prompt", nargs="?", default="以 <Picture 1> 的造型与服饰为准，人物在春日庭院里折下一枝柳条，外观保持一致，近景跟随", help="参考指令")
    parser.add_argument("ratio", nargs="?", default="16:9", help="宽高比")
    return parser.parse_args()


def main():
    MODEL = "agnes-video-2.5-flash"

    args = parse_args()
    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    prompt = args.prompt
    ratio = args.ratio

    images = [media_input.prepare_image(item.strip()) for item in sources if item.strip()]
    if len(images) > 5:
        raise SystemExit("Flash 模式参考图片最多 5 张")

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "mode": "reference",
        "seconds": "12",
        "size": "720P",
        "aspect_ratio": ratio,
        "images": images,
    }

    video_id, _ = video_common.submit(payload)
    final = video_common.poll(video_id, MODEL)
    url = video_common.final_url(final)

    if final.get("status") == "completed" and url:
        print("[完成] 视频已生成")
        print(f"视频地址：{url}")
        media_download.spawn_download(url, "output/videos", 0)
    else:
        print("[失败] 视频未完成：", final.get("error"))
        sys.exit(1)

if __name__ == "__main__":
    main()
