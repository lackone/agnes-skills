#!/usr/bin/env python3
"""按 video_id 查询已有任务：agnes-video-2.5-flash

stdout 仅输出一个结果 JSON；进度与提示走 stderr。

用法：python query-video.py <video_id>
"""
import argparse
import json
import sys

import video_common


def parse_args():
    parser = argparse.ArgumentParser(description="按 video_id 查询已有任务：agnes-video-2.5-flash")
    parser.add_argument("video_id", help="任务 video_id")
    return parser.parse_args()


def main():
    MODEL = "agnes-video-2.5-flash"

    video_id = parse_args().video_id
    final = video_common.poll(video_id, MODEL)
    url = video_common.final_url(final)

    if final.get("status") == "completed" and url:
        print(json.dumps({"ok": True, "url": url, "video_id": video_id}, ensure_ascii=False))
    else:
        print(json.dumps({"ok": False, "error": final.get("error") or "任务未完成"}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
