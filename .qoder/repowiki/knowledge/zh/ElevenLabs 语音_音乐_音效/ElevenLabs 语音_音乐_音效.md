---
kind: external_dependency
name: ElevenLabs 语音/音乐/音效
slug: elevenlabs
category: external_dependency
category_hints:
    - vendor_identity
scope:
    - '**'
source_files:
    - .env.example
    - docs/PROVIDERS.md
---

通过 `ELEVENLABS_API_KEY` 接入 ElevenLabs 的 TTS、音乐生成与音效生成。免费层每月 10,000 字符，超出后按量付费。也可通过 fal.ai 的 `fal_elevenlabs_tts` 间接调用。