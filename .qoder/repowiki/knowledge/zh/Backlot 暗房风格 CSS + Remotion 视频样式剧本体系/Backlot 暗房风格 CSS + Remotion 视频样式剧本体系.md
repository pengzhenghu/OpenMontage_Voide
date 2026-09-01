---
kind: frontend_style
name: Backlot 暗房风格 CSS + Remotion 视频样式剧本体系
category: frontend_style
scope:
    - '**'
source_files:
    - backlot/ui/board.css
    - backlot/ui/index.html
    - backlot/ui/board.html
    - backlot/ui/lib.js
    - backlot/ui/library.js
    - backlot/ui/board.js
    - remotion-composer/package.json
    - styles/playbook_loader.py
    - styles/clean-professional.yaml
    - styles/anime-ghibli.yaml
    - styles/flat-motion-graphics.yaml
    - styles/minimalist-diagram.yaml
    - styles/premium-minimalist.yaml
    - schemas/styles/playbook.schema.json
---

## 1. 系统概览

本仓库包含两套前端/视觉样式系统：
- **Backlot UI**（`backlot/ui/`）：基于原生 HTML/CSS/JS 的本地看板界面，采用“暗房编辑”美学——近黑底色、胶片颗粒噪点、电影场记板图标、打字机字体与暖色强调。
- **Remotion Composer**（`remotion-composer/`）：基于 Remotion + React 的视频合成器，无 Tailwind/组件库，通过 `@remotion/google-fonts` 加载字体，以数据驱动的 TSX 组件渲染动画视频。
- **样式剧本（Style Playbooks）**（`styles/*.yaml` + `styles/playbook_loader.py`）：用 YAML 声明式定义视频输出样式（配色、排版、动效、音频、覆盖层），并通过 Python 加载、校验并做 WCAG 2.1 对比度与色盲安全分析。

三者共同构成 OpenMontage 的“前端样式”能力：Backlot 是编辑时的可视化界面，Remotion 是最终视频输出的渲染引擎，YAML 剧本则是跨两者的设计令牌来源。

## 2. 关键文件

| 路径 | 作用 |
|---|---|
| `backlot/ui/board.css` | Backlot 全部样式，含 CSS 变量主题、暗/亮双主题、入场动画、胶片条、脚本卡片等 |
| `backlot/ui/index.html` / `board.html` | Backlot Library 与 Board 页面入口 |
| `backlot/ui/lib.js` / `library.js` / `board.js` | 纯 JS 逻辑，无框架依赖 |
| `remotion-composer/package.json` | 仅依赖 `remotion`、`react`、`@remotion/*`，无 CSS 框架 |
| `styles/playbook_loader.py` | 样式 YAML 加载、JSON Schema 校验、WCAG 对比度/色盲/排版层级分析 |
| `styles/clean-professional.yaml` 等 | 预设样式剧本（配色、排版、动效、音频、覆盖层、图表调色板） |
| `schemas/styles/playbook.schema.json` | 样式剧本 JSON Schema（由 loader 引用） |

## 3. 架构与设计约定

### 3.1 Backlot UI 的 CSS 设计系统
- **CSS 自定义属性集中管理主题**：`:root` 中定义 `--bg`、`--surface`、`--text`、`--amber`、`--green`、`--red`、`--blue`、`--cream` 等语义化变量；通过 `:root[data-theme="light"]` 切换亮色主题。
- **全局字号缩放**：所有 `font-size` 使用 `calc(<px> * var(--fs-scale))`，通过单一 `--fs-scale` 变量实现整体可读性缩放。
- **字体栈**：`Inter`（正文）、`JetBrains Mono`（代码/标签）、`Courier Prime`（剧本预览区），通过 Google Fonts 引入。
- **暗房美学**：背景 `#0a0a0c`，叠加 SVG 噪声滤镜实现的胶片颗粒（`grain-opacity` 控制），径向渐变暗角（`--bg-vignette`）让媒体内容突出。
- **BEM-like 类名**：`.slate`、`.rail`、`.stage`、`.scene-card`、`.script-card`、`.filmstrip`、`.lib-card`、`.panel`、`.drawer` 等，按语义块组织。
- **响应式策略**：`@media (max-width: 900px)` 将网格布局从 `grid-template-columns: 1fr 320px` 切换为单列，横向滚动阶段轨道，脚本卡片宽度自适应。
- **微交互**：统一的 `rise` 入场动画、`pulse` 状态灯、`shimmer` 生成占位、`travel` 能量流动线、`ringpulse` 活跃节点脉冲。

### 3.2 Remotion 视频样式
- 无 CSS 框架，完全基于 React + Remotion 组件树渲染视频帧。
- 字体通过 `@remotion/google-fonts` 在运行时加载。
- 样式通过 props/data 驱动（如 `titled_video_props.json`、`demo-props/*.json`），而非外部样式表。

### 3.3 样式剧本（Playbook）体系
- **声明式 YAML**：每个 `*.yaml` 定义一个完整视觉风格，包括 `identity`、`visual_language.color_palette`、`typography`、`motion`、`audio`、`asset_generation`、`overlays`、`quality_rules`、`chart_palette`、`color_rules`。
- **运行时加载**：`playbook_loader.load_playbook(name)` 从 `styles/` 或 `styles/custom/` 读取 YAML，调用 `validate_playbook()` 通过 `schemas/styles/playbook.schema.json` 校验。
- **可访问性强制校验**：`validate_contrast()` 计算 WCAG 2.1 对比度（AA/AAA），`check_color_blind_safety()` 模拟红绿/蓝黄色盲混淆，`validate_type_hierarchy()` 检查标题/正文权重差，`validate_accessibility()` 汇总结果。
- **预设剧本**：`clean-professional.yaml`（企业向）、`anime-ghibli.yaml`、`flat-motion-graphics.yaml`、`minimalist-diagram.yaml`、`premium-minimalist.yaml`。

## 4. 约定与约束

- **Backlot 主题必须通过 `data-theme` 属性切换**：CSS 仅监听 `:root[data-theme="light"]`，默认 `html { color-scheme: dark; }`。
- **所有颜色必须走 CSS 变量**：禁止硬编码颜色值到组件样式中，统一通过 `var(--*)` 引用。
- **字号必须遵循 `--fs-scale` 缩放模式**：所有 `font-size` 使用 `calc(px * var(--fs-scale))`，保证可访问性缩放一致。
- **样式剧本必须通过 JSON Schema 校验**：新增 YAML 前需满足 `schemas/styles/playbook.schema.json` 的结构要求，否则 `load_playbook()` 抛出异常。
- **样式剧本必须通过 WCAG 对比度与色盲安全检查**：`validate_accessibility()` 返回的 `pass` 字段用于阻断不合格样式的渲染。
- **Remotion 组件不引入第三方 CSS 框架**：`package.json` 中无 Tailwind、Bootstrap、Ant Design 等依赖，样式完全内联于 TSX 或通过 Remotion 内置能力。
- **Backlot 不使用任何前端框架**：纯 HTML + 原生 CSS + 原生 JS 模块（`type="module"`），通过 FastAPI 静态文件服务暴露。
- **字体统一通过 Google Fonts 加载**：Backlot 使用 `fonts.googleapis.com` 引入 Inter/JetBrains Mono/Courier Prime；Remotion 使用 `@remotion/google-fonts`。
- **暗/亮主题的颜色对必须成对维护**：`board.css` 中 `:root` 与 `:root[data-theme="light"]` 下的对应变量需保持语义一致（如 `--bg` ↔ `--bg`、`--text` ↔ `--text`）。
