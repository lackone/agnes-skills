#!/usr/bin/env python3
"""批量视频生成：并发提交与轮询，只回 URL；下载由独立 download.py 进程完成。

请求输入为 JSON 数组，每个元素：
    {"prompt": "...", "seconds": "5", "size": "720P", "aspect_ratio": "16:9",
     "images": ["..."], "audios": ["..."], "videos": [{"url": "..."}]}

用法：
    python batch-videos.py --request jobs.json
    cat jobs.json | python batch-videos.py --request -
    python batch-videos.py --request jobs.json --concurrency 4

落盘：逐条用独立 download.py <url> <out_dir> [index]，与生成进程解耦，
避免生成脚本退出时内置后台下载线程被中断。
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import load_env
import media_input
import video_common

MODEL = "agnes-video-2.5"


def load_items(source):
    if source == "-":
        return json.load(sys.stdin)
    with open(source, encoding="utf-8") as handle:
        return json.load(handle)


def generate_one(item):
    payload = {
        "model": MODEL,
        "prompt": item["prompt"],
        "seconds": item.get("seconds", "5"),
        "size": item.get("size", "720P"),
        "aspect_ratio": item.get("aspect_ratio", "16:9"),
    }
    images = item.get("images") or []
    audios = item.get("audios") or []
    videos = item.get("videos") or []
    if len(images) > 8:
        raise ValueError("参考图片最多 8 张")
    if len(audios) > 3:
        raise ValueError("参考音频最多 3 段")
    if len(videos) > 1:
        raise ValueError("参考视频最多 1 个")
    if len(images) + len(audios) + len(videos) > 12:
        raise ValueError("单次请求参考媒体总数不超过 12 个")
    if images:
        payload["images"] = [media_input.prepare_image(x) for x in images]
    if audios:
        payload["audios"] = [media_input.prepare_audio(x) for x in audios]
    if videos:
        payload["videos"] = videos
    payload["mode"] = item.get("mode") or (
        "reference" if images or audios or videos else "text"
    )

    video_id, _ = video_common.submit(payload)
    final = video_common.poll(video_id, MODEL)
    return video_common.final_url(final)


def main():
    parser = argparse.ArgumentParser(description="批量视频生成（并发提交，只回 URL）")
    parser.add_argument("--request", default="-", help="JSON 文件路径，或 - 读取标准输入")
    parser.add_argument("--concurrency", type=int, default=None, help="最大并发任务数；默认最多 4 个，可按任务量覆盖")
    args = parser.parse_args()

    load_env.load_env()
    items = load_items(args.request)
    if not isinstance(items, list):
        raise SystemExit("请求输入必须是 JSON 数组")
    if not items:
        raise SystemExit("请求数组为空")
    if args.concurrency is not None and args.concurrency < 1:
        raise SystemExit("--concurrency 需不小于 1")

    workers = args.concurrency or min(len(items), 4)
    results = [None] * len(items)

    # 并发提交并轮询；任一任务完成即先打印其 URL，不在进程内下载。
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
            except (Exception, SystemExit) as exc:  # 单任务失败不影响其他任务
                results[index] = {"ok": False, "error": str(exc)}
                print(f"[失败] 任务 {index + 1}：{exc}")

    print(json.dumps({"results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
