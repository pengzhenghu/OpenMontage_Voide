---
kind: external_dependency
name: Replicate 托管视频模型
slug: replicate
category: external_dependency
category_hints:
    - vendor_identity
scope:
    - '**'
source_files:
    - .env.example
    - docs/PROVIDERS.md
---

通过 `REPLICATE_API_TOKEN` 调用 Replicate 托管的 Seedance 等视频模型，作为 fal.ai 之外的可选备选路径。