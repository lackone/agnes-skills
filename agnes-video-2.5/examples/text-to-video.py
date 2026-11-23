#!/usr/bin/env python3
"""文生视频：agnes-video-2.5

用法：python text-to-video.py [提示词] [时长] [尺寸] [画幅]
"""
import argparse
import sys

import video_common


def parse_args():
    parser = argparse.ArgumentParser(description="文生视频：agnes-video-2.5")
    parser.add_argument("prompt", nargs="?", default="竹林小径上一名素色长衫的人缓步前行，落叶随风掠过，镜头平稳跟拍，阴天柔和散射光", help="内容描述")
    parser.add_argument("seconds", nargs="?", default="5", help="时长（4–12 秒）")
    parser.add_argument("size", nargs="?", default="720P", help="尺寸档位")
    parser.add_argument("ratio", nargs="?", default="16:9", help="宽高比")
    return parser.parse_args()


def main():
    MODEL = "agnes-video-2.5"

    args = parse_args()
    prompt = args.prompt
    seconds = args.seconds
    size = args.size
    ratio = args.ratio

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "mode": "text",
        "seconds": seconds,
        "size": size,
        "aspect_ratio": ratio,
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
