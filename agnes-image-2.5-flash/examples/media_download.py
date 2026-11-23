#!/usr/bin/env python3
"""Download generated media to a local directory (stdlib only).

- Public result URLs are fetched without Authorization headers.
- Streamed write with a per-file size cap and bounded retries on transient errors.
- Retries network hiccups and 408/429/500/502/503/504; honors Retry-After.
- Other HTTP statuses (400/401/403/404/...) fail without retry.
- Extension comes from Content-Type, falling back to the URL suffix.
"""
import os
import sys
import time
import urllib.error
import urllib.request

import http_retry

MAX_MIB_DEFAULT = 512


def _registry_proxies():
    """读取 Windows WinINET 注册表代理；非 Windows / 未启用返回 None。"""
    if sys.platform != "win32":
        return None
    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
        )
        try:
            enable, _ = winreg.QueryValueEx(key, "ProxyEnable")
            if not enable:
                return None
            server, _ = winreg.QueryValueEx(key, "ProxyServer")
        finally:
            winreg.CloseKey(key)
        if not server or not server.strip():
            return None
        server = server.strip()
        proxies = {}
        if "=" in server:
            for part in server.split(";"):
                if "=" in part:
                    scheme, addr = part.split("=", 1)
                    proxies[scheme.strip().lower()] = addr.strip()
        else:
            proxies["http"] = server
            proxies["https"] = server
        for scheme, addr in list(proxies.items()):
            if addr and "://" not in addr:
                proxies[scheme] = "http://" + addr
        return proxies
    except OSError:
        return None


def _opener(use_proxy=True):
    """构造下载 opener。

    - `use_proxy=False`：显式空 ProxyHandler，禁用一切代理，直连。
    - `use_proxy=True`：合并标准库探测到的代理（环境变量；macOS 系统代理经 scutil）与 Windows 注册表代理；都没有则默认 opener（直连）。Linux 仅读环境变量。
    """
    if not use_proxy:
        return urllib.request.build_opener(urllib.request.ProxyHandler({}))
    proxies = dict(urllib.request.getproxies())
    registry = _registry_proxies()
    if registry:
        proxies.update(registry)
    if proxies:
        return urllib.request.build_opener(urllib.request.ProxyHandler(proxies))
    return urllib.request.build_opener()


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


def download_media(url, out_dir, index=0, max_mib=MAX_MIB_DEFAULT, retries=3, use_proxy=True):
    """Download `url` into `out_dir`; return the saved local path.

    Args:
        use_proxy: `True`（默认）自动探测环境变量与系统代理，有则走代理、无则直连；
            `False` 强制直连，忽略一切代理配置。

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
            with _opener(use_proxy).open(request, timeout=300) as resp:
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
