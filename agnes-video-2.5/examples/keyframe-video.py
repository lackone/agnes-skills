#!/usr/bin/env python3
"""首尾帧控制：agnes-video-2.5

stdout 仅输出一个结果 JSON；进度与提示走 stderr。

用法：python keyframe-video.py [首帧URL] [尾帧URL] [提示词] [时长] [尺寸] [画幅]
"""
import argparse
import json
import sys

import video_common


def parse_args():
    parser = argparse.ArgumentParser(description="首尾帧控制：agnes-video-2.5")
    parser.add_argument("first_frame", nargs="?", default="https://example.com/first.png", help="首帧图片 URL")
    parser.add_argument("last_frame", nargs="?", default="https://example.com/last.png", help="尾帧图片 URL")
    parser.add_argument("prompt", nargs="?", default="人物由首帧的坐姿起身，缓步走到画面右侧的画架前，镜头平稳跟随，动作自然地过渡到尾帧", help="过渡指令")
    parser.add_argument("seconds", nargs="?", default="5", help="时长（4–12 秒）")
    parser.add_argument("size", nargs="?", default="720P", help="尺寸档位")
    parser.add_argument("ratio", nargs="?", default="16:9", help="宽高比")
    return parser.parse_args()


def main():
    MODEL = "agnes-video-2.5"

    args = parse_args()
    payload = {
        "model": MODEL,
        "prompt": args.prompt,
        "mode": "keyframe",
        "seconds": args.seconds,
        "size": args.size,
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
