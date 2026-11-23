# agnes-3.0-flash

Agnes 3.0 Flash 文本/视觉对话模型（Agent 编程、工具编排、长任务执行）。

- 模型 ID：`agnes-3.0-flash`
- 端点：`/v1/chat/completions`、`/v1/responses`、`/v1/messages`
- 上下文 512K，最大输出 65,536

## 运行

```bash
python examples/basic-chat.py "用通俗语言解释缓存击穿并给出防范思路"
python examples/image-understanding.py "https://example.com/diagram.png" "图中有哪些关键模块？"
python examples/tool-calling.py "帮我找一下退换货规则在哪份文档里"
python examples/thinking-mode.py "把图书清单页面拆成可逐条验收的开发任务" 2048
```

参数均为可选位置参数，缺省走内置演示；`-h/--help` 查看参数说明。

环境变量 `AGNES_API_KEY`、`AGNES_BASE_URL` 可在 `.env` 或进程环境中配置（模板见套件根目录 `.env.example`；单独拷贝时直接设置环境变量即可）。详细参数见 [SKILL.md](SKILL.md)。
