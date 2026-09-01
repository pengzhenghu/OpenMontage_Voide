---
kind: external_dependency
name: Atlas Cloud 全模态推理网关
slug: atlas-cloud
category: external_dependency
category_hints:
    - vendor_identity
scope:
    - '**'
source_files:
    - .env.example
    - docs/PROVIDERS.md
---

单一 `ATLASCLOUD_API_KEY` 提供统一端点访问 Seedance、MiniMax、Hunyuan、Seedream、GPT Image 2、Nano Banana 2 等多种模型。每个模型的真实 schema 由 OpenMontage 校验，不依赖厂商文档中的后缀或参数名互换。