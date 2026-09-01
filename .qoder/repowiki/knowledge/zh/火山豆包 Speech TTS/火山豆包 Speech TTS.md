---
kind: external_dependency
name: 火山豆包 Speech TTS
slug: doubao-speech
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

通过新控制台 API Key 接入火山引擎 Doubao Speech 2.0，使用 `X-Api-Key` + `X-Api-Resource-Id: seed-tts-2.0` 鉴权，支持长文本异步提交与查询、字符级时间戳。`DOUBAO_SPEECH_VOICE_TYPE` 指定默认音色（如 `zh_female_vv_uranus_bigtts`）。不要将新控制台 Key 误传给 `X-Api-App-Id` 或 `X-Api-Access-Key`。