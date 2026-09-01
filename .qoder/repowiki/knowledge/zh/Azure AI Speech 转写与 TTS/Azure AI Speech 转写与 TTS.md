---
kind: external_dependency
name: Azure AI Speech 转写与 TTS
slug: azure-speech
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

单一 `AZURE_SPEECH_KEY` + `AZURE_SPEECH_REGION` 同时解锁云端 STT（Fast Transcription REST v1，本地音频直传，无需 Blob/SAS）与云端 TTS（SSML 同步 REST）。STT 端点为 `{region}.api.cognitive.microsoft.com/speechtotext/transcriptions:transcribe`，TTS 端点为 `{region}.tts.speech.microsoft.com/cognitiveservices/v1`，两者 host 不同，故 TTS 有独立的 `AZURE_TTS_ENDPOINT` 覆盖变量。