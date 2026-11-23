#!/usr/bin/env python3
"""图片参考：agnes-video-2.5

图片可为本地路径、公共 HTTPS URL 或 Data URI；本地文件会被读成 Data URI 内联提交。
多张图片用英文逗号分隔。
stdout 仅输出一个结果 JSON；进度与提示走 stderr。

用法：python image-reference.py [图片1,图片2,...] [提示词] [时长] [尺寸] [画幅]
"""
import argparse
import json
import sys

import media_input
import video_common


def parse_args():
    parser = argparse.ArgumentParser(description="图片参考：agnes-video-2.5")
    parser.add_argument("sources", nargs="?", default="https://example.com/character.png", help="参考图片，多张用英文逗号分隔")
    parser.add_argument("prompt", nargs="?", default="以 <Picture 1> 的人物造型与服饰为准，她在古镇回廊下驻足看池中游鱼，外观保持一致，中景缓慢横移", help="参考指令")
    parser.add_argument("seconds", nargs="?", default="5", help="时长（4–12 秒）")
    parser.add_argument("size", nargs="?", default="720P", help="尺寸档位")
    parser.add_argument("ratio", nargs="?", default="16:9", help="宽高比")
    return parser.parse_args()


def main():
    MODEL = "agnes-video-2.5"

    args = parse_args()
    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    images = [media_input.prepare_image(item.strip()) for item in sources if item.strip()]
    if len(images) > 8:
        print(json.dumps({"ok": False, "error": "参考图片最多 8 张"}, ensure_ascii=False))
        sys.exit(1)

    payload = {
        "model": MODEL,
        "prompt": args.prompt,
        "mode": "reference",
        "seconds": args.seconds,
        "size": args.size,
        "aspect_ratio": args.ratio,
        "images": images,
    }

    video_id, _ = video_common.submit(payload)
    final = video_common.poll(video_id, MODEL)
    url = video_common.final_url(final)

    if final.get("status") == "completed" and url:
        print(json.dumps({"ok": True, "url": url, "video_id": video_id}, ensure_ascii=False))
    else:
        print(json.dumps({"ok": False, "error": final.get("error") or "视频未完成"}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
