#!/usr/bin/env python3
"""文生图（Base64 输出，直落盘）：agnes-image-2.5-flash

stdout 仅输出一个结果 JSON（含本地 path）；进度与提示走 stderr。

用法：python text-to-image-base64.py [提示词] [尺寸] [--out-dir 绝对路径]
"""
import argparse
import base64
import json
import os
import sys
import time

import http_retry
import load_env


def parse_args():
    parser = argparse.ArgumentParser(description="文生图（Base64 输出）：agnes-image-2.5-flash")
    parser.add_argument("prompt", nargs="?", default="极简木质书架特写，午后阳光斜照在一排书脊上，尘埃在光束里浮动，安静温暖，方形构图", help="生成指令")
    parser.add_argument("size", nargs="?", default="1K", choices=["1K", "2K", "3K", "4K"], help="尺寸档位")
    parser.add_argument("--out-dir", default="images", help="保存目录（默认 images/，相对当前工作目录；调用方应传绝对路径）")
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
        "return_base64": True,
    }

    try:
        result = http_retry.post_json(base, "/images/generations", payload, api_key, timeout=360)
        item = (result.get("data") or [{}])[0]
        b64 = item.get("b64_json")
        if not b64:
            raise ValueError("未返回 Base64 图像")

        out_dir = args.out_dir
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"image-{int(time.time() * 1000)}.png")
        with open(out_path, "wb") as handle:
            handle.write(base64.b64decode(b64))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        sys.exit(1)

    print(json.dumps({"ok": True, "path": os.path.abspath(out_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
