---
kind: external_dependency
name: OpenAI TTS / GPT Image 2
slug: openai
category: external_dependency
category_hints:
    - vendor_identity
scope:
    - '**'
source_files:
    - .env.example
    - docs/PROVIDERS.md
---

通过 `OPENAI_API_KEY` 接入 OpenAI TTS（tts-1/gpt-4o-mini-tts）与 GPT Image 2 图片生成。DALL-E 2/3 已下线，gpt-image-1 家族于 2026-12-01 退役，推荐使用 gpt-image-2。无免费额度，需预付费账单。