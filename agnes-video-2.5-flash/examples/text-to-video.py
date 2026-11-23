#!/usr/bin/env python3
"""文生视频（固定 720P）：agnes-video-2.5-flash

默认 16:9、12 秒；先回 URL，后台异步下载到 output/videos。

用法：python text-to-video.py [提示词] [时长] [画幅]
"""
import argparse
import sys
import threading

import media_download
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
    prompt = args.prompt
    seconds = args.seconds
    ratio = args.ratio

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "mode": "text",
        "seconds": seconds,
        "size": "720P",
        "aspect_ratio": ratio,
    }

    video_id, _ = video_common.submit(payload)
    final = video_common.poll(video_id, MODEL)
    url = video_common.final_url(final)

    if final.get("status") != "completed" or not url:
        print("[失败] 视频未完成：", final.get("error"))
        sys.exit(1)

    print("[完成] 视频已生成")
    print(f"视频地址：{url}")

    def _save():
        try:
            path = media_download.download_media(url, "output/videos", 0)
            print(f"[下载] 视频已保存：{path}")
        except Exception as exc:
            print(f"[下载失败] {exc}")

    thread = threading.Thread(target=_save, daemon=True)
    thread.start()
    thread.join()

if __name__ == "__main__":
    main()
