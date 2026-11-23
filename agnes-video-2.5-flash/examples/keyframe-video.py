#!/usr/bin/env python3
"""首尾帧控制（固定 720P）：agnes-video-2.5-flash

用法：python keyframe-video.py [首帧URL] [尾帧URL] [提示词] [时长]
"""
import argparse
import sys

import video_common


def parse_args():
    parser = argparse.ArgumentParser(description="首尾帧控制（固定 720P）：agnes-video-2.5-flash")
    parser.add_argument("first_frame", nargs="?", default="https://example.com/first.png", help="首帧图片 URL")
    parser.add_argument("last_frame", nargs="?", default="https://example.com/last.png", help="尾帧图片 URL")
    parser.add_argument("prompt", nargs="?", default="人物从首帧姿态回身整理衣袖，缓步走到廊下，镜头缓慢推进并自然过渡到尾帧", help="过渡指令")
    parser.add_argument("seconds", nargs="?", default="12", help="时长（4–12 秒）")
    return parser.parse_args()


def main():
    MODEL = "agnes-video-2.5-flash"

    args = parse_args()
    first_frame = args.first_frame
    last_frame = args.last_frame
    prompt = args.prompt
    seconds = args.seconds

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "mode": "keyframe",
        "seconds": seconds,
        "size": "720P",
        "aspect_ratio": "16:9",
        "first_frame": first_frame,
        "last_frame": last_frame,
    }

    video_id, _ = video_common.submit(payload)
    final = video_common.poll(video_id, MODEL)
    url = video_common.final_url(final)

    if final.get("status") == "completed" and url:
        print("[完成] 视频已生成")
        print(f"视频地址：{url}")
    else:
        print("[失败] 视频未完成：", final.get("error"))
        sys.exit(1)

if __name__ == "__main__":
    main()
