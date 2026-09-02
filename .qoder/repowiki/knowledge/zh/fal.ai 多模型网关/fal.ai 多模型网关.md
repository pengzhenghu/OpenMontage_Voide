---
kind: external_dependency
name: fal.ai 多模型网关
slug: fal-ai
category: external_dependency
category_hints:
    - vendor_identity
    - sdk_real_api
scope:
    - '**'
source_files:
    - .env.example
    - docs/PROVIDERS.md
---

OpenMontage 通过 `FAL_KEY`（或别名 `FAL_AI_API_KEY`）接入 fal.ai，作为图片与视频生成的统一入口：FLUX/Recraft/Seedream 图片、Kling/Veo/MiniMax/Hunyuan/Gemini Omni 视频、以及 ElevenLabs 语音/音乐。该 key 是性价比最高的单 key 覆盖方案，被 `video_selector` / `image_selector` 优先推荐。
- 认证方式：Bearer token，直接放入 `.env`。
- 注意：同一 key 同时解锁多个供应商，但各模型的计费、分辨率、时长上限不同，需按文档确认当前定价后再批量调用。