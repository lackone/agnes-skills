#!/usr/bin/env python3
"""基础对话示例：agnes-3.0-flash

用法：python basic-chat.py [提问]
"""
import argparse
import json

import http_retry
import load_env


def parse_args():
    parser = argparse.ArgumentParser(description="基础对话示例：agnes-3.0-flash")
    parser.add_argument("question", nargs="?", default="用通俗语言解释什么是缓存击穿，并给出一个防范思路。", help="用户提问")
    return parser.parse_args()


def main():
    args = parse_args()
    load_env.load_env()
    api_key = load_env.api_key()
    base = load_env.base_url()

    question = args.question

    payload = {
        "model": "agnes-3.0-flash",
        "messages": [
            {"role": "system", "content": "你是一名回答简洁、论据清楚的技术助手。"},
            {"role": "user", "content": question},
        ],
        "temperature": 0.7,
        "max_tokens": 1024,
    }

    result = http_retry.post_json(base, "/chat/completions", payload, api_key, timeout=120)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\n回复：")
    print(result["choices"][0]["message"]["content"])

if __name__ == "__main__":
    main()
