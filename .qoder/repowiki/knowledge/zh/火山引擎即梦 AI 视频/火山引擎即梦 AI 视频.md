---
kind: external_dependency
name: 火山引擎即梦 AI 视频
slug: volcengine-jimeng
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

通过 Volcengine IAM AK/SK 对 visual.volcengineapi.com 发起 HMAC-SHA256 V4 签名的即梦 3.0 Pro 文生/图生视频。通用路由为 `CVSync2Async*`（版本 `2022-08-31`），`req_key` 为 `jimeng_ti2v_v30_pro`，成功码 `10000`，任务状态包括 `in_queue`、`generating`、`done`、`not_found`、`expired`。输入约束：prompt ≤800 字符，frames 必须为 121（5s）或 241（10s），seed 为 -1 或 ≥0 整数。