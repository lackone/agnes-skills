#!/usr/bin/env python3
"""视频参考：agnes-video-2.5

参考视频只接受可公开访问的 URL，不做本地 Data URI 内联。

用法：python video-reference.py [参考视频URL] [提示词] [时长] [尺寸] [画幅] [起始秒数]
"""
import argparse
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
    source = args.source
    prompt = args.prompt
    seconds = args.seconds
    size = args.size
    ratio = args.ratio
    start_seconds = args.start_seconds
    if start_seconds < 0:
        raise SystemExit("start_seconds 不能为负数")

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "mode": "reference",
        "seconds": seconds,
        "size": size,
        "aspect_ratio": ratio,
        "videos": [
            {"url": source, "start_seconds": start_seconds, "require_audio": False}
        ],
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
