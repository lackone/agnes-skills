#!/usr/bin/env python3
"""Load variables from .env without overriding existing process environment.

Search order (process environment always wins over files):
  1. AGNES_ENV_FILE (explicit env file, when set; no fallback)
  2. current working directory .env
  3. examples/.env (script directory)
  4. skill root/.env
  5. suite root/.env

Supported keys:
  AGNES_API_KEY
  AGNES_BASE_URL
"""
import os


def _load_file(path):
    try:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except OSError:
        pass


def load_env():
    here = os.path.dirname(os.path.abspath(__file__))
    explicit = os.environ.get("AGNES_ENV_FILE")
    if explicit:
        _load_file(explicit)
        return
    candidates = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(here, ".env"),
        os.path.join(os.path.dirname(here), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(here)), ".env"),
    ]
    for path in candidates:
        _load_file(path)


def api_key():
    key = os.environ.get("AGNES_API_KEY")
    if not key:
        raise SystemExit(
            "未配置 API Key：请设置环境变量 AGNES_API_KEY，或在 .env 中填写。"
        )
    return key


def base_url():
    base = (os.environ.get("AGNES_BASE_URL")
            or "https://apihub.agnes-ai.com/v1").rstrip("/")
    if not base.endswith("/v1"):
        base += "/v1"
    return base
