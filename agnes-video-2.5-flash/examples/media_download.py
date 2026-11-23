#!/usr/bin/env python3
"""Download generated media to a local directory (stdlib only).

- Public result URLs are fetched without Authorization headers.
- Streamed write with a per-file size cap and bounded retries on transient errors.
- Retries network hiccups and 408/429/500/502/503/504; honors Retry-After.
- Other HTTP statuses (400/401/403/404/...) fail without retry.
- Extension comes from Content-Type, falling back to the URL suffix.
"""
import os
import threading
import time
import urllib.error
import urllib.request

import http_retry

MAX_MIB_DEFAULT = 512

_CONTENT_EXT = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "video/mp4": ".mp4",
    "video/webm": ".webm",
    "audio/mpeg": ".mp3",
}
_URL_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".webm", ".mp3")


def _ext_from_url(url):
    path = url.split("?", 1)[0].lower()
    for ext in _URL_EXT:
        if path.endswith(ext):
            return ext
    return ""


def _retry_after(header):
    if not header:
        return None
    try:
        return float(header)
    except (TypeError, ValueError):
        return None


def download_media(url, out_dir, index=0, max_mib=MAX_MIB_DEFAULT, retries=3):
    """Download `url` into `out_dir`; return the saved local path.

    Raises after the final retry, or when the file exceeds `max_mib`.
    """
    os.makedirs(out_dir, exist_ok=True)
    target = None
    last_error = None

    for attempt in range(retries + 1):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "agnes-skills/1.0"},
            )
            with urllib.request.urlopen(request, timeout=300) as resp:
                content_type = resp.headers.get("Content-Type", "").split(";", 1)[0].strip()
                ext = _CONTENT_EXT.get(content_type) or _ext_from_url(url) or ".bin"
                target = os.path.join(
                    out_dir, f"media-{index:02d}-{int(time.time() * 1000)}{ext}"
                )
                size = 0
                with open(target, "wb") as handle:
                    while True:
                        chunk = resp.read(256 * 1024)
                        if not chunk:
                            break
                        size += len(chunk)
                        if size > max_mib * 1024 * 1024:
                            handle.close()
                            os.remove(target)
                            raise ValueError(f"下载超过 {max_mib} MiB 上限")
                        handle.write(chunk)
            return target
        except urllib.error.HTTPError as exc:
            if target and os.path.exists(target):
                os.remove(target)
            target = None
            if exc.code in http_retry.RETRYABLE_STATUS and attempt < retries:
                retry_after = _retry_after(exc.headers.get("Retry-After"))
                time.sleep(retry_after if retry_after is not None else min(2 ** attempt, 10))
                continue
            raise OSError(f"下载失败 HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if target and os.path.exists(target):
                os.remove(target)
            target = None
            if attempt < retries:
                time.sleep(min(2 ** attempt, 10))
                continue
            raise

    raise last_error


def spawn_download(url, out_dir, index=0):
    """后台 daemon 线程下载，不阻塞调用方；URL 先行交付，落盘结果异步打印。"""
    def _save():
        try:
            path = download_media(url, out_dir, index)
            print(f"[下载] 已保存：{path}")
        except Exception as exc:
            print(f"[下载失败] {exc}")

    thread = threading.Thread(target=_save, daemon=True)
    thread.start()
    return thread
