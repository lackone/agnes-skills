#!/usr/bin/env python3
"""首尾帧控制（固定 720P）：agnes-video-2.5-flash

stdout 仅输出一个结果 JSON；进度与提示走 stderr。

用法：python keyframe-video.py [首帧URL] [尾帧URL] [提示词] [时长] [画幅]
"""
import argparse
import json
import sys

import video_common


def parse_args():
    parser = argparse.ArgumentParser(description="首尾帧控制（固定 720P）：agnes-video-2.5-flash")
    parser.add_argument("first_frame", nargs="?", default="https://example.com/first.png", help="首帧图片 URL")
    parser.add_argument("last_frame", nargs="?", default="https://example.com/last.png", help="尾帧图片 URL")
    parser.add_argument("prompt", nargs="?", default="人物从首帧姿态回身整理衣袖，缓步走到廊下，镜头缓慢推进并自然过渡到尾帧", help="过渡指令")
    parser.add_argument("seconds", nargs="?", default="12", help="时长（4–12 秒）")
    parser.add_argument("ratio", nargs="?", default="16:9", help="宽高比")
    return parser.parse_args()


def main():
    MODEL = "agnes-video-2.5-flash"

    args = parse_args()
    payload = {
        "model": MODEL,
        "prompt": args.prompt,
        "mode": "keyframe",
        "seconds": args.seconds,
        "size": "720P",
        "aspect_ratio": args.ratio,
        "first_frame": args.first_frame,
        "last_frame": args.last_frame,
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
