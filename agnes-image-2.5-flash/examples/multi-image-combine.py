#!/usr/bin/env python3
"""多图合成：agnes-image-2.5-flash

两张参考图可为本地路径、公共 HTTPS URL 或 Data URI；本地文件会被读成 Data URI 内联提交。
stdout 仅输出一个结果 JSON；进度与提示走 stderr。

用法：python multi-image-combine.py [图片1] [图片2] [提示词] [尺寸] [比例]
"""
import argparse
import json
import sys

import http_retry
import load_env
import media_input


def parse_args():
    parser = argparse.ArgumentParser(description="多图合成：agnes-image-2.5-flash")
    parser.add_argument("image1", nargs="?", default="https://example.com/character-1.png", help="第一张参考图")
    parser.add_argument("image2", nargs="?", default="https://example.com/character-2.png", help="第二张参考图")
    parser.add_argument("prompt", nargs="?", default="把两位参考人物安排在同一张茶席上，左侧沏茶、右侧捧杯，竹帘作背景，淡彩国风，光线柔和", help="合成指令")
    parser.add_argument("size", nargs="?", default="1K", choices=["1K", "2K", "3K", "4K"], help="尺寸档位")
    parser.add_argument("ratio", nargs="?", default="16:9", help="宽高比")
    return parser.parse_args()


def main():
    args = parse_args()
    load_env.load_env()
    api_key = load_env.api_key()
    base = load_env.base_url()

    image_uris = [media_input.prepare_image(args.image1), media_input.prepare_image(args.image2)]

    payload = {
        "model": "agnes-image-2.5-flash",
        "prompt": args.prompt,
        "size": args.size,
        "ratio": args.ratio,
        "extra_body": {
            "image": image_uris,
            "response_format": "url",
        },
    }

    try:
        result = http_retry.post_json(base, "/images/generations", payload, api_key, timeout=360)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        sys.exit(1)

    image_url = (result.get("data") or [{}])[0].get("url")
    if not image_url:
        print(json.dumps({"ok": False, "error": "未返回图片地址"}, ensure_ascii=False))
        sys.exit(1)

    print(json.dumps({"ok": True, "url": image_url}, ensure_ascii=False))


if __name__ == "__main__":
    main()
