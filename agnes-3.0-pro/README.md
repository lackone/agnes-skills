# agnes-3.0-pro

Agnes 3.0 Pro 长上下文推理模型（智能体任务、文档分析、科学编码、长上下文整合）。

- 模型 ID：`agnes-3.0-pro`
- 端点：`/v1/chat/completions`、`/v1/responses`、`/v1/messages`
- 上下文 1M，最大输出 256K，带推理；付费模型

## 运行

```bash
python examples/basic-chat.py "说明乐观锁与悲观锁分别适合什么场景"
python examples/image-understanding.py "https://example.com/chart.png" "总结图表并指出异常"
python examples/responses-api.py "解释智能体为什么需要借助工具获取外部信息" 1024
python examples/thinking-mode.py "梳理单体演进到微服务的迁移步骤与风险" 2048
```

参数均为可选位置参数，缺省走内置演示；`-h/--help` 查看参数说明。

环境变量 `AGNES_API_KEY`、`AGNES_BASE_URL` 可在 `.env` 或进程环境中配置（模板见套件根目录 `.env.example`；单独拷贝时直接设置环境变量即可）。详细参数见 [MODULE.md](MODULE.md)。
