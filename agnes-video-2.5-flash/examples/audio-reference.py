#!/usr/bin/env python3
"""音频参考（固定 720P，最多 3 段）：agnes-video-2.5-flash

音频可为本地路径、公共 HTTPS URL 或 Data URI；本地文件会被读成 Data URI 内联提交。
多段音频用英文逗号分隔。注意：音频只参考节奏、氛围与动作节拍，不克隆音色、口音，也不承担台词配音。
stdout 仅输出一个结果 JSON；进度与提示走 stderr。

用法：python audio-reference.py [音频1,音频2,...] [提示词] [时长] [画幅]
"""
import argparse
import json
import sys

import media_input
import video_common


def parse_args():
    parser = argparse.ArgumentParser(description="音频参考（固定 720P）：agnes-video-2.5-flash")
    parser.add_argument("sources", nargs="?", default="https://example.com/reference-audio.mp3", help="参考音频，多段用英文逗号分隔")
    parser.add_argument("prompt", nargs="?", default="跟随 <Audio 1> 的节奏起伏安排镜头长短与画面切换，傍晚河岸步道行人缓缓经过，氛围松弛", help="参考指令")
    parser.add_argument("seconds", nargs="?", default="12", help="时长（4–12 秒）")
    parser.add_argument("ratio", nargs="?", default="16:9", help="宽高比")
    return parser.parse_args()


def main():
    MODEL = "agnes-video-2.5-flash"

    args = parse_args()
    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    audios = [media_input.prepare_audio(item.strip()) for item in sources if item.strip()]
    if len(audios) > 3:
        print(json.dumps({"ok": False, "error": "Flash 模式参考音频最多 3 段"}, ensure_ascii=False))
        sys.exit(1)

    payload = {
        "model": MODEL,
        "prompt": args.prompt,
        "mode": "reference",
        "seconds": args.seconds,
        "size": "720P",
        "aspect_ratio": args.ratio,
        "audios": audios,
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
