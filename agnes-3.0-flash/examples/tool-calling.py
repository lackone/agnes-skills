#!/usr/bin/env python3
"""函数调用请求与解析示例：agnes-3.0-flash

本脚本只演示工具定义、发起请求和解析 tool_calls；
拿到调用请求后应由应用侧执行函数，再把结果回填到对话中下一轮提交。

用法：python tool-calling.py [提问]
"""
import argparse
import json

import http_retry
import load_env


def parse_args():
    parser = argparse.ArgumentParser(description="函数调用请求与解析示例：agnes-3.0-flash")
    parser.add_argument("question", nargs="?", default="帮我找一下退换货规则写在哪份内部文档里。", help="用户提问")
    return parser.parse_args()


def main():
    args = parse_args()
    load_env.load_env()
    api_key = load_env.api_key()
    base = load_env.base_url()

    question = args.question

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_docs",
                "description": "在内部知识库中按关键词检索文档条目。",
                "parameters": {
                    "type": "object",
                    "properties": {"keyword": {"type": "string", "description": "检索关键词"}},
                    "required": ["keyword"],
                },
            },
        }
    ]

    payload = {
        "model": "agnes-3.0-flash",
        "messages": [{"role": "user", "content": question}],
        "tools": tools,
    }

    result = http_retry.post_json(base, "/chat/completions", payload, api_key, timeout=120)

    print(json.dumps(result, indent=2, ensure_ascii=False))

    message = result["choices"][0]["message"]
    calls = message.get("tool_calls")
    if calls:
        print("\n模型请求调用工具：")
        for call in calls:
            fn = call["function"]
            print(f"  {fn['name']}({fn['arguments']})")
    else:
        print("\n模型回复：")
        print(message.get("content") or "")

if __name__ == "__main__":
    main()
