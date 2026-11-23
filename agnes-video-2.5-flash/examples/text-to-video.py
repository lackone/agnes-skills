#!/usr/bin/env python3
"""文生视频（固定 720P）：agnes-video-2.5-flash

默认 16:9、12 秒；只回 URL，下载由独立 download.py 进程完成。
stdout 仅输出一个结果 JSON；进度与提示走 stderr。

用法：python text-to-video.py [提示词] [时长] [画幅]
"""
import argparse
import json
import sys

import video_common


def parse_args():
    parser = argparse.ArgumentParser(description="文生视频（固定 720P）：agnes-video-2.5-flash")
    parser.add_argument("prompt", nargs="?", default="海边栈道上一只白鹭收翅落在栏杆上，海浪缓慢拍岸，固定长镜头，清晨薄雾", help="内容描述")
    parser.add_argument("seconds", nargs="?", default="12", help="时长（4–12 秒）")
    parser.add_argument("ratio", nargs="?", default="16:9", help="宽高比")
    return parser.parse_args()


def main():
    MODEL = "agnes-video-2.5-flash"

    args = parse_args()
    payload = {
        "model": MODEL,
        "prompt": args.prompt,
        "mode": "text",
        "seconds": args.seconds,
        "size": "720P",
        "aspect_ratio": args.ratio,
    }

    video_id, _ = video_common.submit(payload)
    final = video_common.poll(video_id, MODEL)
    url = video_common.final_url(final)

    if final.get("status") != "completed" or not url:
        print(json.dumps({"ok": False, "error": final.get("error") or "视频未完成"}, ensure_ascii=False))
        sys.exit(1)

    print(json.dumps({"ok": True, "url": url, "video_id": video_id}, ensure_ascii=False))


if __name__ == "__main__":
    main()
