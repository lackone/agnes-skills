#!/usr/bin/env python3
"""文生图（URL 输出）：agnes-image-2.5-flash

默认 16:9、1K；只回 URL，下载由独立 download.py 进程完成。
stdout 仅输出一个结果 JSON；进度与提示走 stderr。

用法：python text-to-image.py [提示词] [尺寸] [比例]
"""
import argparse
import json
import sys

import http_retry
import load_env


def parse_args():
    parser = argparse.ArgumentParser(description="文生图（URL 输出）：agnes-image-2.5-flash")
    parser.add_argument("prompt", nargs="?", default="江南古镇清晨，石拱桥横跨河面，白墙黑瓦间升起淡淡炊烟，水面有薄雾，水墨质感，横幅构图", help="生成指令")
    parser.add_argument("size", nargs="?", default="1K", choices=["1K", "2K", "3K", "4K"], help="尺寸档位")
    parser.add_argument("ratio", nargs="?", default="16:9", help="宽高比")
    return parser.parse_args()


def main():
    args = parse_args()
    load_env.load_env()
    api_key = load_env.api_key()
    base = load_env.base_url()

    payload = {
        "model": "agnes-image-2.5-flash",
        "prompt": args.prompt,
        "size": args.size,
        "ratio": args.ratio,
        "extra_body": {"response_format": "url"},
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
