#!/usr/bin/env python3
"""Shared submit + poll helpers for Agnes Video 2.5 Flash (stdlib only).

Transient conditions (network errors and 408/429/500/502/503/504) are
retried by `http_retry` with Retry-After aware backoff and a shared 429
cooldown. Non-retryable responses (400/401/403/404/...) surface as
`http_retry.HttpError` and are not retried.

进度与调试信息写 stderr，保持 stdout 可供上层脚本输出唯一结果 JSON。
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import http_retry
import load_env


def _post(url, payload):
    load_env.load_env()
    api_key = load_env.api_key()
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        result = http_retry.request_json(req, timeout=120)
        return 200, result
    except http_retry.HttpError as exc:
        return exc.status, exc.body


def submit(payload):
    """Create a video task; return (video_id, raw_response)."""
    base = load_env.base_url()
    status, result = _post(f"{base}/videos", payload)
    print(f"HTTP {status}", file=sys.stderr)
    print(json.dumps(result, indent=2, ensure_ascii=False), file=sys.stderr)
    if status >= 400:
        message = result.get("detail") or result.get("message") or "任务创建失败"
        raise SystemExit(f"任务创建失败：{message}")
    video_id = result.get("video_id") or result.get("task_id") or result.get("id")
    if not video_id:
        raise SystemExit("响应中未获取到 video_id")
    return video_id, result


def poll(video_id, model_name, interval=2, max_seconds=600):
    """Poll /agnesapi until completed or failed; return final response."""
    load_env.load_env()
    base = load_env.base_url().replace("/v1", "")
    api_key = load_env.api_key()
    deadline = time.time() + max_seconds
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        query = urllib.parse.urlencode({"video_id": video_id, "model_name": model_name})
        req = urllib.request.Request(
            f"{base}/agnesapi?{query}",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        try:
            result = http_retry.request_json(req, retries=2, timeout=30)
        except http_retry.HttpError as exc:
            if exc.status in http_retry.RETRYABLE_STATUS:
                print(f"poll {attempt} 瞬态错误 {exc.status}，下一轮继续：{exc}", file=sys.stderr)
                time.sleep(interval)
                continue
            raise SystemExit(str(exc))
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"poll {attempt} 网络抖动，下一轮继续：{exc}", file=sys.stderr)
            time.sleep(interval)
            continue
        status = result.get("status")
        progress = result.get("progress", 0)
        print(f"[{attempt}] status={status} progress={progress}", file=sys.stderr)
        if status in ("completed", "failed"):
            return result
        time.sleep(interval)
    raise SystemExit("轮询超时")


def final_url(result):
    return (
        result.get("url")
        or (result.get("metadata") or {}).get("url")
        or result.get("video_url")
    )
