---
kind: external_dependency
name: 阿里云百炼 DashScope
slug: dashscope
category: external_dependency
category_hints:
    - vendor_identity
scope:
    - '**'
source_files:
    - .env.example
    - docs/PROVIDERS.md
---

通过 `DASHSCOPE_API_KEY` 接入 Qwen-Image 图片生成、Qwen-TTS 中文旁白、以及带词级时间戳的 Qwen-ASR 语音识别（用于字幕对齐）。DashScope 的 `/compatible-mode/v1/` 仅支持 chat/embeddings，图片/TTS/ASR 均使用 DashScope 原生端点，非 OpenAI 兼容路径。