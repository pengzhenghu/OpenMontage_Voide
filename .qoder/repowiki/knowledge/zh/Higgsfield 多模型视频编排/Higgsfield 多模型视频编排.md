---
kind: external_dependency
name: Higgsfield 多模型视频编排
slug: higgsfield
category: external_dependency
category_hints:
    - vendor_identity
scope:
    - '**'
source_files:
    - .env.example
    - docs/PROVIDERS.md
---

通过 `HIGGSFIELD_API_KEY` + `HIGGSFIELD_API_SECRET`（或合并键 `HIGGSFIELD_KEY=key:secret`）接入 Higgsfield，路由 Kling 3.0、Veo 3.1、Sora 2、WAN 2.5、Soul Cinema 等模型，并提供 Soul ID 跨片段角色一致性。API 访问需 Starter 及以上订阅。