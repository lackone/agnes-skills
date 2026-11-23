#!/usr/bin/env python3
"""批量文生图：并发提交，只回 URL；下载由独立 download.py 进程完成。

请求输入为 JSON 数组，每个元素：
    {"prompt": "...", "size": "1K", "ratio": "16:9"}

用法：
    python batch-images.py --request prompts.json
    cat prompts.json | python batch-images.py --request -
    python batch-images.py --request prompts.json --concurrency 8

落盘：逐条用独立 download.py <url> <out_dir> [index]，与生成进程解耦，
避免生成脚本退出时内置后台下载线程被中断。
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import http_retry
import load_env

IMAGE_MODEL = "agnes-image-2.5-flash"


def load_items(source):
    if source == "-":
        return json.load(sys.stdin)
    with open(source, encoding="utf-8") as handle:
        return json.load(handle)


def generate_one(item):
    base = load_env.base_url()
    api_key = load_env.api_key()
    payload = {
        "model": IMAGE_MODEL,
        "prompt": item["prompt"],
        "size": item.get("size", "1K"),
        "ratio": item.get("ratio", "16:9"),
        "extra_body": {"response_format": "url"},
    }
    result = http_retry.post_json(base, "/images/generations", payload, api_key, timeout=360)
    return (result.get("data") or [{}])[0].get("url")


def main():
    parser = argparse.ArgumentParser(description="批量文生图（并发提交，只回 URL）")
    parser.add_argument("--request", default="-", help="JSON 文件路径，或 - 读取标准输入")
    parser.add_argument("--concurrency", type=int, default=None, help="最大并发任务数；默认最多 8 个，可按任务量覆盖")
    args = parser.parse_args()

    load_env.load_env()
    items = load_items(args.request)
    if not isinstance(items, list):
        raise SystemExit("请求输入必须是 JSON 数组")
    if not items:
        raise SystemExit("请求数组为空")
    if args.concurrency is not None and args.concurrency < 1:
        raise SystemExit("--concurrency 需不小于 1")

    workers = args.concurrency or min(len(items), 8)
    results = [None] * len(items)

    # 并发提交生成任务；任一任务完成即先打印其 URL，不在进程内下载。
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(generate_one, item): i for i, item in enumerate(items)}
        for future in as_completed(futures):
            index = futures[future]
            try:
                url = future.result()
                if not url:
                    raise ValueError("未返回成片地址")
                results[index] = {"ok": True, "url": url}
                print(f"[完成] 任务 {index + 1}：{url}")
            except Exception as exc:  # 单任务失败不影响其他任务
                results[index] = {"ok": False, "error": str(exc)}
                print(f"[失败] 任务 {index + 1}：{exc}")

    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
