#!/usr/bin/env python3
"""图像理解示例：agnes-3.0-pro

用法：python image-understanding.py [图片URL] [追问]
"""
import argparse
import json

import http_retry
import load_env


def parse_args():
    parser = argparse.ArgumentParser(description="图像理解示例：agnes-3.0-pro")
    parser.add_argument("image_url", nargs="?", default="https://example.com/chart.png", help="公开可访问的图片 URL")
    parser.add_argument("question", nargs="?", default="总结这张图表传达的信息，并指出其中异常或需要关注的点。", help="追问内容")
    return parser.parse_args()


def main():
    args = parse_args()
    load_env.load_env()
    api_key = load_env.api_key()
    base = load_env.base_url()

    image_url = args.image_url
    question = args.question

    payload = {
        "model": "agnes-3.0-pro",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        "max_tokens": 1200,
    }

    result = http_retry.post_json(base, "/chat/completions", payload, api_key, timeout=120)

    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("\n回复：")
    print(result["choices"][0]["message"]["content"])

if __name__ == "__main__":
    main()
