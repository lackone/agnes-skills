#!/usr/bin/env python3
"""图生图：agnes-image-2.5-flash

输入可为本地图片路径、公共 HTTPS URL 或 Data URI；本地文件会被读成 Data URI 内联提交。

用法：python image-to-image.py [输入图片] [提示词] [尺寸] [比例]
"""
import argparse
import json
import sys

import http_retry
import load_env
import media_input


def parse_args():
    parser = argparse.ArgumentParser(description="图生图：agnes-image-2.5-flash")
    parser.add_argument("source", nargs="?", default="https://example.com/input-image.png", help="输入图片路径、URL 或 Data URI")
    parser.add_argument("prompt", nargs="?", default="保留原有人物姿态与构图，把背景替换为雪后初晴的古镇茶馆，整体调成暖色调胶片质感", help="编辑指令")
    parser.add_argument("size", nargs="?", default="1K", choices=["1K", "2K", "3K", "4K"], help="尺寸档位")
    parser.add_argument("ratio", nargs="?", default="16:9", help="宽高比")
    return parser.parse_args()


def main():
    args = parse_args()
    load_env.load_env()
    api_key = load_env.api_key()
    base = load_env.base_url()

    source = args.source
    prompt = args.prompt
    size = args.size
    ratio = args.ratio

    source_uri = media_input.prepare_image(source)

    payload = {
        "model": "agnes-image-2.5-flash",
        "prompt": prompt,
        "size": size,
        "ratio": ratio,
        "extra_body": {
            "image": [source_uri],
            "response_format": "url",
        },
    }

    result = http_retry.post_json(base, "/images/generations", payload, api_key, timeout=360)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    image_url = (result.get("data") or [{}])[0].get("url")
    if not image_url:
        print("[失败] 未返回图片地址")
        sys.exit(1)
    print("[完成] 图生图结束")
    print(f"图片地址：{image_url}")

if __name__ == "__main__":
    main()
