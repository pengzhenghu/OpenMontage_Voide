---
kind: external_dependency
name: Google TTS / Imagen / Lyria / Gemini Omni / Veo
slug: google-ai-studio
category: external_dependency
category_hints:
    - vendor_identity
    - auth_protocol
scope:
    - '**'
source_files:
    - .env.example
    - docs/PROVIDERS.md
---

单一 `GOOGLE_API_KEY`（或 `GEMINI_API_KEY` 优先）同时解锁 Google Cloud TTS（700+ 声音、50+ 语言）、Imagen 4 图片、Lyria 音乐、Gemini Omni Flash 视频（含对话式编辑）、以及直连 Veo 视频。TTS 需额外启用 Text-to-Speech API；Imagen/Lyria/Omni/Veo 需启用 Generative Language API。也可用 `GOOGLE_APPLICATION_CREDENTIALS` 服务账户 JSON 文件进行认证，并配置 `GOOGLE_CLOUD_PROJECT` 与 `GOOGLE_CLOUD_LOCATION`。