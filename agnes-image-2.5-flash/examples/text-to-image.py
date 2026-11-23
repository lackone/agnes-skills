#!/usr/bin/env python3
"""文生图（URL 输出）：agnes-image-2.5-flash

默认 16:9、2K；先回 URL，后台异步下载到 output/images。

用法：python text-to-image.py [提示词] [尺寸] [比例]
"""
import argparse
import json
import sys

import http_retry
import load_env
import media_download


def parse_args():
    parser = argparse.ArgumentParser(description="文生图（URL 输出）：agnes-image-2.5-flash")
    parser.add_argument("prompt", nargs="?", default="江南古镇清晨，石拱桥横跨河面，白墙黑瓦间升起淡淡炊烟，水面有薄雾，水墨质感，横幅构图", help="生成指令")
    parser.add_argument("size", nargs="?", default="2K", choices=["1K", "2K", "3K", "4K"], help="尺寸档位")
    parser.add_argument("ratio", nargs="?", default="16:9", help="宽高比")
    return parser.parse_args()


def main():
    args = parse_args()
    load_env.load_env()
    api_key = load_env.api_key()
    base = load_env.base_url()

    prompt = args.prompt
    size = args.size
    ratio = args.ratio

    payload = {
        "model": "agnes-image-2.5-flash",
        "prompt": prompt,
        "size": size,
        "ratio": ratio,
        "extra_body": {"response_format": "url"},
    }

    result = http_retry.post_json(base, "/images/generations", payload, api_key, timeout=360)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    image_url = (result.get("data") or [{}])[0].get("url")
    if not image_url:
        print("[失败] 未返回图片地址")
        sys.exit(1)
    print("[完成] 图片已生成")
    print(f"图片地址：{image_url}")

    # 后台异步下载，不阻塞 URL 交付；主线程打印地址后即返回。
    media_download.spawn_download(image_url, "output/images", 0)

if __name__ == "__main__":
    main()
