---
kind: external_dependency
name: 火山引擎 Ark Seedance 2.0/2.5 直连
slug: volcengine-ark-seedance
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

绕过 fal.ai/Replicate，直接调用火山引擎 Ark 平台的 Seedance 2.0 Standard/Fast/Mini 与 2.5 模型。`ARK_API_KEY` 仅传 key body（不含 `Bearer ` 前缀），由工具在请求时自动添加授权头。支持文本/首帧图/多模态参考到视频，异步任务创建→轮询→下载流程。Seedance 2.5 最多接受 3 张图、10 个视频、10 个音频参考；本地视频输入因公开 API 未声明 Data URI 支持而被拒绝，需改用 HTTPS URL 或 Ark 资源引用。