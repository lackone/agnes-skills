#!/usr/bin/env python3
"""Thinking 模式示例（Anthropic 兼容 thinking 字段）：agnes-3.0-pro

用法：python thinking-mode.py [问题] [budget_tokens]
"""
import argparse
import json

import http_retry
import load_env


def parse_args():
    parser = argparse.ArgumentParser(description="Thinking 模式示例：agnes-3.0-pro")
    parser.add_argument("question", nargs="?", default="梳理一次从单体架构演进到微服务的迁移步骤与主要风险。", help="问题描述")
    parser.add_argument("budget", nargs="?", type=int, default=2048, help="思考预算 Token 数")
    return parser.parse_args()


def main():
    args = parse_args()
    load_env.load_env()
    api_key = load_env.api_key()
    base = load_env.base_url()

    question = args.question
    budget = args.budget

    payload = {
        "model": "agnes-3.0-pro",
        "messages": [{"role": "user", "content": question}],
        "max_tokens": budget + 1024,
        "thinking": {"type": "enabled", "budget_tokens": budget},
    }

    result = http_retry.post_json(base, "/chat/completions", payload, api_key, timeout=180)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\n回复：")
    print(result["choices"][0]["message"]["content"])

if __name__ == "__main__":
    main()
