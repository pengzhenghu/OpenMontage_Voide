---
kind: logging_system
name: 基于 Python stdlib logging 的分散式日志与 Backlot 事件流
category: logging_system
scope:
    - '**'
source_files:
    - lib/events.py
    - tools/base_tool.py
    - lib/source_media_review.py
    - lib/checkpoint.py
    - backlot/server.py
    - tools/audio/google_music.py
    - tools/audio/music_gen.py
    - tools/graphics/google_imagen.py
    - tools/graphics/image_selector.py
---

## 1. 使用的系统/方法

OpenMontage 没有引入第三方日志框架（如 loguru、structlog、sentry、datadog），而是**直接使用 Python 标准库 `logging`**。仓库中未发现任何全局 logger 初始化（无 `logging.basicConfig`、无自定义 Handler/Formatter/Filter），也没有集中式的日志配置入口。各模块按需 `import logging`，通过 `logging.getLogger(__name__)` 获取模块级 logger 并调用 `warning()` / `info()` 等。

此外，项目还维护了一套独立的**结构化事件流**（Backlot event stream）：工具执行时自动向每个项目的 `events.jsonl` 追加 JSON 行，供 Backlot 看板实时消费，这属于可观测性层面的“应用日志”，而非传统控制台日志。

## 2. 关键文件与位置

- `lib/events.py`：Backlot 事件写入/读取核心，定义 `emit_event`、`read_events`、`infer_project_dir`，将 `{ts, tool, scene_id, depth, event, output_path, success, cost_usd, duration_s, error}` 等字段以 JSONL 形式追加到 `projects/<project>/events.jsonl`。
- `tools/base_tool.py`：所有工具的基类 `BaseTool`，通过 `__init_subclass__` 自动用 `_instrument_execute` 装饰每个 `execute()`，在 start/error/finish 三处调用 `lib.events.emit_event`；该装饰器对异常完全吞掉（“Observability must never break production”），确保事件层失败不影响工具执行。
- `lib/source_media_review.py`：使用 `logger = logging.getLogger(__name__)` 记录 `audio_probe` / `ffprobe` / `frame_sampler` 失败的警告信息。
- `lib/checkpoint.py`：在检查点加载/保存失败时通过 `logging.getLogger(__name__).warning(...)` 输出警告。
- `tools/audio/google_music.py`、`tools/audio/music_gen.py`、`tools/graphics/google_imagen.py`、`tools/graphics/image_selector.py` 等工具模块：各自 `import logging` 后用 `logging.getLogger(__name__).warning/info(...)` 记录工具内部状态。
- `backlot/server.py`：消费 `events.jsonl` 并通过 SSE `/api/project/{id}/events` 推送给前端；本身不产生应用日志。

## 3. 架构与约定

### 3.1 控制台日志（Python `logging`）
- **无全局配置**：仓库未在任何启动路径调用 `basicConfig`，因此所有 `logging` 调用遵循 Python 默认行为——若无 root handler 则输出到 stderr（且仅显示 WARNING 及以上级别）。实际生产/开发环境需由部署方或上层进程负责配置。
- **模块级 logger**：惯例是 `logger = logging.getLogger(__name__)`，然后 `logger.warning("...", args...)` 使用 `%` 风格占位符（如 `"audio_probe failed for %s: %s", path, e`），避免字符串拼接开销。
- **级别选择**：当前代码几乎全部使用 `warning()`，未见 `debug()` / `error()` / `info()` 的系统化使用模式，说明日志主要用于记录“可恢复的异常/降级路径”。

### 3.2 结构化事件流（Backlot events.jsonl）
- **触发点**：所有继承自 `BaseTool` 的工具在执行 `execute()` 时，被 `_instrument_execute` 自动注入 start/finish/error 三个事件。
- **项目归属推断**：`infer_project_dir` 从输入参数中按优先级匹配 `project_dir` / `project_path` / `output_path` / `input_path` / `video_path` / `audio_path` / `image_path` / `file_path`，并校验路径必须位于 `PROJECTS_DIR` 下，防止误写。
- **并发安全**：使用线程锁 `_write_lock` 保证同一进程内多工具线程的追加顺序；跨进程追加无同步，但依赖 O_APPEND 原子追加 + 读端跳过损坏行的容错设计。
- **零负担原则**：注释明确“Observability must never break production: every public function swallows its own errors”，任何事件写入异常都被静默丢弃。
- **字段规范**：每条事件包含 `ts`（UTC ISO）、`tool`、`scene_id`、`depth`（嵌套深度，用于去重统计）、`event`（start/finish/error）、`output_path`、`success`、`cost_usd`、`duration_s`、`error`。

### 3.3 与 Backlot 看板的集成
- Backlot 服务通过 watchfiles 监听 `projects/` 目录变更，当 `events.jsonl` 变化时通过 SSE `/api/project/{id}/events` 推送 change 事件，前端据此刷新活动列表和场景状态。
- 事件流与文件系统解耦：工具只写 `events.jsonl`，Backlot 只读，互不阻塞。

## 4. 约定与约束

- **禁止引入第三方日志库**：仓库未安装/导入任何第三方日志框架，所有日志均基于 stdlib `logging`。
- **事件层不可失败**：`lib/events.py` 中 `emit_event` 包裹完整 try/except 吞掉所有异常；`_instrument_execute` 同样保证事件层失败不影响工具执行。这是硬性约束，不是建议。
- **项目归属必须落在 `projects/` 下**：`infer_project_dir` 显式拒绝不在 `PROJECTS_DIR` 下的路径，防止误写到其他目录。
- **JSONL 格式稳定**：`EVENTS_FILENAME = "events.jsonl"`，字段名固定为 `ts/tool/scene_id/depth/event/output_path/success/cost_usd/duration_s/error`，由 `base_tool.py` 和 `events.py` 共同约定。
- **日志级别策略**：当前代码仅使用 `warning()` 记录可恢复错误；未见统一的 debug/info 策略，新增日志应沿用此模式。
- **测试隔离**：测试套件通过 socket 拦截禁止真实网络访问，因此工具日志中关于外部 API 调用的 warning 在测试环境中通常不会出现。
- **示例代码中的 `logging.basicConfig`**：仅出现在 `.agents/skills/bfl-api/references/code-examples/python-client.py` 等参考文档中，不属于工程运行时代码，不应视为仓库约定。