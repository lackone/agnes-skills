#!/usr/bin/env python3
"""批量文生图：并发提交，先回 URL，再后台下载到本地。

请求输入为 JSON 数组，每个元素：
    {"prompt": "...", "size": "2K", "ratio": "16:9"}

用法：
    python batch-images.py --request prompts.json
    cat prompts.json | python batch-images.py --request -
    python batch-images.py --request prompts.json --concurrency 4 --no-download
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import http_retry
import load_env
import media_download

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
        "size": item.get("size", "2K"),
        "ratio": item.get("ratio", "16:9"),
        "extra_body": {"response_format": "url"},
    }
    result = http_retry.post_json(base, "/images/generations", payload, api_key, timeout=360)
    return (result.get("data") or [{}])[0].get("url")


def main():
    parser = argparse.ArgumentParser(description="批量文生图（并发提交 + 后台下载）")
    parser.add_argument("--request", default="-", help="JSON 文件路径，或 - 读取标准输入")
    parser.add_argument("--concurrency", type=int, default=None, help="最大并发任务数；默认按任务数开线程（一条任务一个线程）")
    parser.add_argument("--output", default="output/batch-images", help="本地下载目录")
    parser.add_argument("--no-download", action="store_true", help="只返回 URL，不落盘")
    args = parser.parse_args()

    items = load_items(args.request)
    if not isinstance(items, list):
        raise SystemExit("请求输入必须是 JSON 数组")
    if not items:
        raise SystemExit("请求数组为空")
    if args.concurrency is not None and args.concurrency < 1:
        raise SystemExit("--concurrency 需不小于 1")

    workers = args.concurrency or len(items)
    results = [None] * len(items)

    # 并发提交生成任务；任一任务完成即先打印其 URL。
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(generate_one, item): i for i, item in enumerate(items)}
        for future in as_completed(futures):
            index = futures[future]
            try:
                url = future.result()
                results[index] = {"ok": True, "url": url}
                print(f"[完成] 任务 {index + 1}：{url}")
            except Exception as exc:  # 单任务失败不影响其他任务
                results[index] = {"ok": False, "error": str(exc)}
                print(f"[失败] 任务 {index + 1}：{exc}")

    # 后台并发下载；生成 URL 已在上面先行返回，下载不阻塞交付。
    if not args.no_download:
        with ThreadPoolExecutor(max_workers=3) as download_pool:
            download_futures = {}
            for index, result in enumerate(results):
                if result and result.get("url"):
                    future = download_pool.submit(
                        media_download.download_media, result["url"], args.output, index
                    )
                    download_futures[future] = index
            for future in as_completed(download_futures):
                index = download_futures[future]
                try:
                    results[index]["local_path"] = future.result()
                    print(f"[下载] 任务 {index + 1} 已保存：{results[index]['local_path']}")
                except Exception as exc:
                    results[index]["download_error"] = str(exc)
                    print(f"[下载失败] 任务 {index + 1}：{exc}")

    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
