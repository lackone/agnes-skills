#!/usr/bin/env python3
"""基础对话示例：agnes-3.0-pro

用法：python basic-chat.py [提问]
"""
import argparse
import json

import http_retry
import load_env


def parse_args():
    parser = argparse.ArgumentParser(description="基础对话示例：agnes-3.0-pro")
    parser.add_argument("question", nargs="?", default="说明数据库乐观锁与悲观锁分别适合什么场景，各举一个典型例子。", help="用户提问")
    return parser.parse_args()


def main():
    args = parse_args()
    load_env.load_env()
    api_key = load_env.api_key()
    base = load_env.base_url()

    question = args.question

    payload = {
        "model": "agnes-3.0-pro",
        "messages": [
            {"role": "system", "content": "你是一名注重严谨性的技术顾问。"},
            {"role": "user", "content": question},
        ],
        "temperature": 0.3,
        "max_tokens": 1200,
    }

    result = http_retry.post_json(base, "/chat/completions", payload, api_key, timeout=120)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\n回复：")
    print(result["choices"][0]["message"]["content"])

if __name__ == "__main__":
    main()
