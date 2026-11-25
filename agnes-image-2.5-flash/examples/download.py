#!/usr/bin/env python3
"""独立下载入口：由调度方作为后台独立进程拉起，落盘后退出。

生成脚本只回 URL；本脚本单独负责把成片下载到本地，生命周期与生成脚本解耦，
避免生成脚本退出时内置后台下载线程被中断。

stdout 仅输出一个结果 JSON；进度与提示走 stderr。

用法：python download.py <url> [out_dir=images] [index] [--no-proxy]
"""
import argparse
import json
import os
import sys

import media_download


def main():
    parser = argparse.ArgumentParser(description="独立下载成片到本地目录")
    parser.add_argument("url", help="成片结果 URL")
    parser.add_argument("out_dir", nargs="?", default="images", help="本地保存目录（默认 images/，相对当前工作目录；调用方应传绝对路径）")
    parser.add_argument("index", nargs="?", default="0", help="序号（文件名前缀）")
    parser.add_argument("--no-proxy", action="store_true", help="强制直连，不走代理")
    args = parser.parse_args()
    try:
        path = media_download.download_media(
            args.url, args.out_dir, int(args.index), use_proxy=not args.no_proxy
        )
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        sys.exit(1)
    print(json.dumps({"ok": True, "path": os.path.abspath(path), "index": int(args.index)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
