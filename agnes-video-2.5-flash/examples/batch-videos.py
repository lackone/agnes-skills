#!/usr/bin/env python3
"""批量视频生成（Flash，固定 720P）：并发提交与轮询，先回 URL，再后台下载。

请求输入为 JSON 数组，每个元素：
    {"prompt": "...", "seconds": "12", "aspect_ratio": "16:9",
     "images": ["..."], "audios": ["..."]}

用法：
    python batch-videos.py --request jobs.json
    cat jobs.json | python batch-videos.py --request -
    python batch-videos.py --request jobs.json --concurrency 4 --no-download
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import load_env
import media_download
import media_input
import video_common

MODEL = "agnes-video-2.5-flash"


def load_items(source):
    if source == "-":
        return json.load(sys.stdin)
    with open(source, encoding="utf-8") as handle:
        return json.load(handle)


def generate_one(item):
    payload = {
        "model": MODEL,
        "prompt": item["prompt"],
        "seconds": item.get("seconds", "12"),
        "size": "720P",
        "aspect_ratio": item.get("aspect_ratio", "16:9"),
    }
    images = item.get("images")
    audios = item.get("audios")
    if images:
        if len(images) > 5:
            raise ValueError("Flash 模式参考图片最多 5 张")
        payload["images"] = [media_input.prepare_image(x) for x in images]
    if audios:
        if len(audios) > 3:
            raise ValueError("Flash 模式参考音频最多 3 段")
        payload["audios"] = [media_input.prepare_audio(x) for x in audios]
    payload["mode"] = item.get("mode") or ("reference" if images or audios else "text")

    video_id, _ = video_common.submit(payload)
    final = video_common.poll(video_id, MODEL)
    return video_common.final_url(final)


def main():
    parser = argparse.ArgumentParser(description="批量视频生成 Flash（并发提交 + 后台下载）")
    parser.add_argument("--request", default="-", help="JSON 文件路径，或 - 读取标准输入")
    parser.add_argument("--concurrency", type=int, default=None, help="最大并发任务数；默认最多 4 个，可按任务量覆盖")
    parser.add_argument("--output", default="output/batch-videos", help="本地下载目录")
    parser.add_argument("--no-download", action="store_true", help="只返回 URL，不落盘")
    args = parser.parse_args()

    items = load_items(args.request)
    if not isinstance(items, list):
        raise SystemExit("请求输入必须是 JSON 数组")
    if not items:
        raise SystemExit("请求数组为空")
    if args.concurrency is not None and args.concurrency < 1:
        raise SystemExit("--concurrency 需不小于 1")

    workers = args.concurrency or min(len(items), 4)
    results = [None] * len(items)
    download_futures = {}

    # 下载池与生成并行：任务一出 URL 即提交下载，不等其余任务生成完。
    download_pool = None if args.no_download else ThreadPoolExecutor(max_workers=4)

    # 并发提交并轮询；任一任务完成即先打印其 URL。
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
                if download_pool:
                    df = download_pool.submit(
                        media_download.download_media, url, args.output, index
                    )
                    download_futures[df] = index
            except (Exception, SystemExit) as exc:  # 单任务失败不影响其他任务
                results[index] = {"ok": False, "error": str(exc)}
                print(f"[失败] 任务 {index + 1}：{exc}")

    # 收集后台下载结果；URL 已先行返回，下载不阻塞交付。
    if download_pool:
        download_pool.shutdown(wait=True)
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
