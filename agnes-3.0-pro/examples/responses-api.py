#!/usr/bin/env python3
"""Responses API 示例：agnes-3.0-pro

用法：python responses-api.py [输入] [max_output_tokens]
"""
import argparse
import json

import http_retry
import load_env


def parse_args():
    parser = argparse.ArgumentParser(description="Responses API 示例：agnes-3.0-pro")
    parser.add_argument("user_input", nargs="?", default="解释智能体为什么需要借助工具获取外部信息，而不是只依赖自身参数。", help="输入内容")
    parser.add_argument("max_output", nargs="?", type=int, default=1024, help="最大输出 Token 数")
    return parser.parse_args()


def main():
    args = parse_args()
    load_env.load_env()
    api_key = load_env.api_key()
    base = load_env.base_url()

    user_input = args.user_input
    max_output = args.max_output

    payload = {
        "model": "agnes-3.0-pro",
        "input": user_input,
        "max_output_tokens": max_output,
    }

    result = http_retry.post_json(base, "/responses", payload, api_key, timeout=180)

    print(json.dumps(result, indent=2, ensure_ascii=False))

    parts = []
    for item in result.get("output", []):
        if item.get("type") == "message":
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    parts.append(content.get("text", ""))

    print("\n回复：")
    print("".join(parts))

if __name__ == "__main__":
    main()
