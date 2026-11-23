#!/usr/bin/env python3
"""按 video_id 查询已有任务：agnes-video-2.5-flash

用法：python query-video.py <video_id>
"""
import argparse
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
        print("[完成] 任务已结束")
        print(f"视频地址：{url}")
    else:
        print("[失败] 任务未完成：", final.get("error"))
        sys.exit(1)

if __name__ == "__main__":
    main()
