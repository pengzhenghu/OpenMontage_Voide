---
kind: external_dependency
name: Runway Gen-4 及第三方模型网关
slug: runway
category: external_dependency
category_hints:
    - vendor_identity
    - client_constraint
scope:
    - '**'
source_files:
    - .env.example
    - docs/PROVIDERS.md
---

通过 `RUNWAY_API_KEY` 接入 Runway 原生 Gen-4 系列以及文档化的第三方模型（Seedance 2.5、Gemini Omni Flash、MiniMax H3/Hailuo 3.0）。API 访问需要付费订阅（Standard 及以上），免费额度仅一次性 125 credits。Gen-3 Alpha Turbo 与 Gen-4 Aleph 已于 2026-07-30 从 API 移除。