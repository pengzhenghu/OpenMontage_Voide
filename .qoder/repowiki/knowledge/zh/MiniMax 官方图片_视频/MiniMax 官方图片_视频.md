---
kind: external_dependency
name: MiniMax 官方图片/视频
slug: minimax
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

通过 `MINIMAX_API_KEY` 接入 MiniMax 一方图片生成与 MiniMax H3 视频（v2 task 契约：`POST /v2/video_generation` → `GET /v2/query/video_generation/{task_id}`），支持 4–15 秒 2K 片段、图文音多模态参考。`MINIMAX_REGION=global|cn` 选择全球或中国大陆路由，`MINIMAX_BASE_URL` 可覆盖私有/企业端点。