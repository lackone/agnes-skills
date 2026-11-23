#!/usr/bin/env python3
"""视频参考：agnes-video-2.5

参考视频只接受可公开访问的 URL，不做本地 Data URI 内联。
stdout 仅输出一个结果 JSON；进度与提示走 stderr。

用法：python video-reference.py [参考视频URL] [提示词] [时长] [尺寸] [画幅] [起始秒数]
"""
import argparse
import json
import sys

import video_common


def parse_args():
    parser = argparse.ArgumentParser(description="视频参考：agnes-video-2.5")
    parser.add_argument("source", nargs="?", default="https://example.com/input.mp4", help="参考视频 URL")
    parser.add_argument("prompt", nargs="?", default="沿用 <Video 1> 的动作时序与镜头衔接，把场景换成清晨的天台花园，主体动作保持连贯", help="参考指令")
    parser.add_argument("seconds", nargs="?", default="5", help="时长（4–12 秒）")
    parser.add_argument("size", nargs="?", default="720P", help="尺寸档位")
    parser.add_argument("ratio", nargs="?", default="16:9", help="宽高比")
    parser.add_argument("start_seconds", nargs="?", type=float, default=0, help="参考视频起始秒数")
    return parser.parse_args()


def main():
    MODEL = "agnes-video-2.5"

    args = parse_args()
    if args.start_seconds < 0:
        print(json.dumps({"ok": False, "error": "start_seconds 不能为负数"}, ensure_ascii=False))
        sys.exit(1)

    payload = {
        "model": MODEL,
        "prompt": args.prompt,
        "mode": "reference",
        "seconds": args.seconds,
        "size": args.size,
        "aspect_ratio": args.ratio,
        "videos": [
            {"url": args.source, "start_seconds": args.start_seconds, "require_audio": False}
        ],
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
