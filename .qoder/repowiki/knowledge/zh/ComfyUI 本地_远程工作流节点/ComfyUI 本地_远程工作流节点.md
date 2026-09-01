---
kind: external_dependency
name: ComfyUI 本地/远程工作流节点
slug: comfyui
category: external_dependency
category_hints:
    - client_constraint
scope:
    - '**'
source_files:
    - .env.example
    - docs/PROVIDERS.md
---

可选的 ComfyUI 服务器地址覆盖（默认 localhost:8188），用于运行 ComfyUI 工作流（含 Partner Nodes 托管节点）。Partner Nodes 仍需联网、登录 Comfy 账号并消耗预付费 credits。