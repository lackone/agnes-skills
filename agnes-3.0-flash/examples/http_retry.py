#!/usr/bin/env python3
"""Retry / rate-limit / error-classification helpers (stdlib only).

Retryable transient conditions:
  - Network: DNS/connection failure, timeout, temporary OSError
  - HTTP: 408, 429, 500, 502, 503, 504

Backoff prefers the server's `Retry-After` header; otherwise exponential
backoff capped at 30s. A shared 429 cooldown applies across threads in one process.
Non-retryable responses (400/401/403/404/...) raise `HttpError` without retry.
"""
import json
import threading
import time
import urllib.error
import urllib.request

RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}

_cooldown_until = 0.0
_cooldown_lock = threading.Lock()


class HttpError(Exception):
    """Non-retryable or finally failed HTTP response."""

    def __init__(self, status, body, message):
        self.status = status
        self.body = body
        self.message = message
        super().__init__(message)


def _safe_json(text):
    try:
        return json.loads(text) if text else {}
    except json.JSONDecodeError:
        return {"raw": text}


def _retry_after(header):
    if not header:
        return None
    try:
        return float(header)
    except (TypeError, ValueError):
        return None


def _describe(status, body):
    summary = body.get("detail") or body.get("message") or "" if isinstance(body, dict) else ""
    if status in (401, 403):
        return f"鉴权失败（HTTP {status}）：检查 API Key 与模型权限"
    if status == 404:
        return f"资源不存在（HTTP {status}）"
    if status == 400:
        return f"请求参数被拒绝（HTTP 400）：{summary or '见响应详情'}"
    if status == 429:
        return "触发限流（HTTP 429）"
    if status >= 500:
        return f"服务端错误（HTTP {status}）"
    return f"HTTP {status}: {summary or '未知错误'}"


def _cooldown_wait():
    with _cooldown_lock:
        wait = _cooldown_until - time.time()
    if wait > 0:
        time.sleep(wait)


def _cooldown_set(seconds):
    global _cooldown_until
    with _cooldown_lock:
        _cooldown_until = max(_cooldown_until, time.time() + seconds)


def _sleep(resp, attempt, base_delay):
    retry_after = _retry_after(resp.headers.get("Retry-After")) if resp else None
    if retry_after is not None:
        delay = min(max(retry_after, 0), 60)
    else:
        delay = min(base_delay * (2 ** attempt), 30)
    time.sleep(delay)


def request_json(request, retries=3, base_delay=1.0, timeout=120):
    """Execute a urllib Request and return parsed JSON.

    Retries transient network/HTTP errors; raises `HttpError` on a
    non-retryable response or after the final retry.
    """
    last_error = None
    for attempt in range(retries + 1):
        _cooldown_wait()
        try:
            with urllib.request.urlopen(request, timeout=timeout) as resp:
                text = resp.read().decode("utf-8", "replace")
                return _safe_json(text)
        except urllib.error.HTTPError as exc:
            body = _safe_json(exc.read().decode("utf-8", "replace"))
            if exc.code in RETRYABLE_STATUS and attempt < retries:
                if exc.code == 429:
                    _cooldown_set(_retry_after(exc.headers.get("Retry-After")) or base_delay * 4)
                _sleep(exc, attempt, base_delay)
                last_error = HttpError(exc.code, body, _describe(exc.code, body))
                continue
            raise HttpError(exc.code, body, _describe(exc.code, body)) from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if attempt < retries:
                _sleep(None, attempt, base_delay)
                last_error = exc
                continue
            raise
    raise last_error


def post_json(base_url, path, payload, api_key, timeout=120, retries=3):
    """Build a JSON POST request and run it through `request_json`."""
    request = urllib.request.Request(
        f"{base_url}{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    return request_json(request, retries=retries, timeout=timeout)
