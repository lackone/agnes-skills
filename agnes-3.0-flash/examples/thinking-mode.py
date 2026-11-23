#!/usr/bin/env python3
"""Thinking 模式示例（OpenAI 兼容格式）：agnes-3.0-flash

用法：python thinking-mode.py [问题] [max_tokens]
"""
import argparse
import json

import http_retry
import load_env


def parse_args():
    parser = argparse.ArgumentParser(description="Thinking 模式示例：agnes-3.0-flash")
    parser.add_argument("question", nargs="?", default="把一个支持标签筛选的图书清单页面，拆成可逐条验收的开发任务。", help="问题描述")
    parser.add_argument("max_tokens", nargs="?", type=int, default=2048, help="最大输出 Token 数")
    return parser.parse_args()


def main():
    args = parse_args()
    load_env.load_env()
    api_key = load_env.api_key()
    base = load_env.base_url()

    question = args.question
    max_tokens = args.max_tokens

    payload = {
        "model": "agnes-3.0-flash",
        "messages": [{"role": "user", "content": question}],
        "max_tokens": max_tokens,
        "chat_template_kwargs": {"enable_thinking": True},
    }

    result = http_retry.post_json(base, "/chat/completions", payload, api_key, timeout=180)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\n回复：")
    print(result["choices"][0]["message"]["content"])

if __name__ == "__main__":
    main()
