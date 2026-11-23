#!/usr/bin/env python3
"""音频参考：agnes-video-2.5

音频可为本地路径、公共 HTTPS URL 或 Data URI；本地文件会被读成 Data URI 内联提交。
多段音频用英文逗号分隔。注意：音频只参考节奏、氛围与动作节拍，不克隆音色、口音，也不承担台词配音。

用法：python audio-reference.py [音频1,音频2,...] [提示词] [时长] [尺寸] [画幅]
"""
import argparse
import sys

import media_input
import video_common


def parse_args():
    parser = argparse.ArgumentParser(description="音频参考：agnes-video-2.5")
    parser.add_argument("sources", nargs="?", default="https://example.com/reference-audio.mp3", help="参考音频，多段用英文逗号分隔")
    parser.add_argument("prompt", nargs="?", default="参照 <Audio 1> 的节拍快慢与氛围起伏安排画面剪辑，白天集市摊位依次掠过，转场自然连贯", help="参考指令")
    parser.add_argument("seconds", nargs="?", default="5", help="时长（4–12 秒）")
    parser.add_argument("size", nargs="?", default="720P", help="尺寸档位")
    parser.add_argument("ratio", nargs="?", default="16:9", help="宽高比")
    return parser.parse_args()


def main():
    MODEL = "agnes-video-2.5"

    args = parse_args()
    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    prompt = args.prompt
    seconds = args.seconds
    size = args.size
    ratio = args.ratio

    audios = [media_input.prepare_audio(item.strip()) for item in sources if item.strip()]
    if len(audios) > 3:
        raise SystemExit("参考音频最多 3 段")

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "mode": "reference",
        "seconds": seconds,
        "size": size,
        "aspect_ratio": ratio,
        "audios": audios,
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
