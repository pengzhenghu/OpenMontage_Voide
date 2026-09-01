---
kind: external_dependency
name: 可灵官方直连 API
slug: kling-official-api
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

独立于 fal.ai 的 Kling 官方路径，使用 `Authorization: Bearer <KLING_API_KEY>` 直调新控制台 API，提供视频、图片、TTS、数字人、对口型能力。默认端点为新加坡 `https://api-singapore.klingai.com`，中国大陆账号可通过 `KLING_API_BASE_URL` 切换至北京端点。Provider 名称为 `kling_official`，与 fal.ai 的 `kling` 路由完全隔离。