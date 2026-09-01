---
kind: external_dependency
name: Suno 完整歌曲生成
slug: suno
category: external_dependency
category_hints:
    - vendor_identity
scope:
    - '**'
source_files:
    - .env.example
    - README.md
---

通过 `SUNO_API_KEY` 接入 Suno 生成带人声歌词的完整歌曲（器乐/任意流派，最长 8 分钟），用于视频配乐。