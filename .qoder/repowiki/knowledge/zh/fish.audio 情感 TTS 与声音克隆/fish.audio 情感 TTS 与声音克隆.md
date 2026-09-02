---
kind: external_dependency
name: fish.audio 情感 TTS 与声音克隆
slug: fish-audio
category: external_dependency
category_hints:
    - vendor_identity
scope:
    - '**'
source_files:
    - .env.example
    - docs/PROVIDERS.md
---

通过 `FISH_AUDIO_API_KEY` 接入 fish.audio S2 系列 TTS，支持内联情绪标签（`[laugh]`、`[whispers]`）与 80+ 语言，并通过 `reference_id` 复用已克隆的声音模型。`model` 为必填参数，无默认值；`s2.1-pro-free` 促销期截至 2026-08-31，之后回退到付费定价。计费按 UTF-8 字节而非字符计算。