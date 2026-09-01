---
kind: error_handling
name: OpenMontage 错误处理体系：结构化异常、重试策略与幂等工具结果
category: error_handling
scope:
    - '**'
source_files:
    - tools/base_tool.py
    - tools/_kling/errors.py
    - backlot/server.py
    - lib/checkpoint.py
    - lib/events.py
    - tests/test_network_guard.py
    - tools/video/atlas_video.py
---

## 1. 总体方案

OpenMontage 在 Python 层采用**分层错误模型**：
- **基础设施层**（`tools/base_tool.py`）定义统一的 `BaseTool` 抽象、`ToolResult` 返回值、`DependencyError`、`ToolCommandError`，以及通过装饰器 `_instrument_execute` 自动注入 Backlot 事件追踪。
- **供应商适配层**（如 `tools/_kling/errors.py`）为每个外部 API 定义领域错误类型（`KlingAPIError`），并集中维护可重试错误码集合 `_RETRYABLE_CODES` 与 HTTP 状态集合 `_RETRYABLE_HTTP`，提供 `is_retryable_kling_error()` 判定函数。
- **HTTP 服务层**（`backlot/server.py`）使用 FastAPI 的 `HTTPException` 表达 400/403/404 等语义化响应，并通过自定义 middleware 控制缓存行为；SSE 流中用 `asyncio.TimeoutError` 发送心跳。
- **流水线校验层**（`lib/checkpoint.py`）定义 `CheckpointValidationError`，用于强制阶段门禁（gate）、前置依赖、风格剧本合法性与 JSON Schema 校验失败。
- **观测层**（`lib/events.py`）遵循“观测不可破坏生产”原则：`emit_event` / `read_events` 内部吞掉所有异常，确保事件写入失败不影响主流程。

## 2. 关键文件与包

| 文件 | 职责 |
|---|---|
| `tools/base_tool.py` | `BaseTool`、`ToolResult`、`RetryPolicy`、`DependencyError`、`ToolCommandError`、执行装饰器 |
| `tools/_kling/errors.py` | `KlingAPIError` + 可重试错误判定 |
| `backlot/server.py` | FastAPI 路由、`HTTPException`、SSE 心跳、路径穿越防护 |
| `lib/checkpoint.py` | `CheckpointValidationError`、阶段门禁、前置依赖校验、JSON Schema 校验 |
| `lib/events.py` | 项目级 `events.jsonl` 追加日志，绝对不抛错 |
| `tests/test_network_guard.py` | 网络守卫测试，证明付费调用在测试中被阻断 |
| `tools/video/atlas_video.py` | 工具级错误归一化：捕获 `AtlasError`/`ValueError`/`KeyError` 后返回 `ToolResult(success=False, ...)` |

## 3. 架构与约定

### 3.1 工具统一返回 `ToolResult`
所有 `BaseTool.execute()` 应返回 `ToolResult`（含 `success`、`error`、`cost_usd`、`duration_seconds`、`artifacts` 等字段）。非致命错误（如缺少 API Key、下游 API 报错）以 `success=False` + `error` 字符串形式返回，而不是抛出异常。这使上层编排器可以统一处理成功/失败分支，无需 try/except 包裹每个工具调用。

### 3.2 可重试错误显式声明
`RetryPolicy` 数据类包含 `max_retries`、`backoff_seconds`、`retryable_errors` 列表。例如 `AtlasVideo` 声明 `retry_policy = RetryPolicy(max_retries=2, retryable_errors=["rate_limit", "timeout"])`。供应商特定错误（如 `KlingAPIError`）通过 `is_retryable_kling_error()` 基于白名单错误码 `{"1302","1303","5000","5001","5002"}` 和 HTTP 状态 `{500,503,504}` 判断是否安全重试。

### 3.3 子进程命令错误包装
`BaseTool.run_command()` 将 `subprocess.CalledProcessError` 包装为 `ToolCommandError`，保留 `returncode`、`cmd`、`output`、`stderr` 并在 `__str__` 中附加 `detail`，便于诊断。

### 3.4 依赖检查抛出 `DependencyError`
`check_dependencies()` 检测 `cmd:`/`binary:`/`env:`/`python:` 依赖缺失时抛出 `DependencyError`，`get_status()` 捕获该异常并映射到 `ToolStatus.UNAVAILABLE`。

### 3.5 流水线门禁与校验抛出 `CheckpointValidationError`
`write_checkpoint()` 在以下情况抛出 `CheckpointValidationError`：
- 阶段不在当前 pipeline manifest 允许列表中
- 未满足前置阶段完成/审批要求（PREREQUISITE VIOLATION）
- 标记为需要人工审批的阶段被直接写为 `completed` 且 `human_approved=False`（GATE VIOLATION）
- 风格剧本名称无效或无法加载
- 产物未通过 JSON Schema 校验

### 3.6 FastAPI 层使用 `HTTPException`
路径穿越尝试返回 403（`path escapes project`），未知项目返回 404（`unknown project: {id}`），媒体不存在返回 404（`media not found`）。SSE 流中通过 `asyncio.TimeoutError` 定期发送心跳事件，连接断开时优雅退出。

### 3.7 观测层零故障保证
`lib/events.py` 的 `emit_event()` 对任何异常（导入失败、路径不存在、写入失败、JSON 序列化失败）都 `pass`；`read_events()` 跳过损坏行。设计注释明确：“Observability must never break production”。

### 3.8 工具级错误归一化
`atlas_video.py` 的 `execute()` 用 `try/except (AtlasError, ValueError, KeyError)` 捕获下游错误，统一返回 `ToolResult(success=False, error=...)`，避免异常冒泡到编排层。

## 4. 约定与约束

- **工具必须返回 `ToolResult`**：由 `BaseTool.execute` 抽象方法强制，所有工具实现遵循此契约。
- **可重试错误必须白名单化**：`_RETRYABLE_CODES` 与 `_RETRYABLE_HTTP` 显式列出允许重试的错误码，禁止默认重试所有错误。
- **网关/门禁违反必须抛 `CheckpointValidationError`**：阶段顺序、人工审批、前置依赖的违规是硬错误，不允许静默降级。
- **事件写入永远不抛错**：`emit_event` 内部 `except Exception: pass`，这是代码中明确的设计规则。
- **FastAPI 路由只抛 `HTTPException`**：所有客户端错误通过 `status_code` + `detail` 表达，不使用裸 `raise Exception`。
- **测试禁用真实网络**：`tests/test_network_guard.py` 断言 socket 连接被拦截，付费工具即使有真实 API Key 也返回 `success=False` 且 `cost_usd == 0.0`，防止测试误消费。
- **子进程输出强制 UTF-8 解码**：`run_command()` 使用 `encoding="utf-8", errors="replace"` 避免 Windows 上因 locale 导致的 UnicodeDecodeError 吞掉真实错误。
- **管道阶段名必须来自 manifest**：`get_pipeline_stages()` 从 YAML manifest 解析阶段顺序，未知 pipeline_type 会抛 `CheckpointValidationError`（fail-closed），而非静默回退。

## 5. 不适用场景说明

本仓库没有前端 UI 框架的错误边界（React 组件中的错误处理属于 Remotion Composer 的前端渲染逻辑，不在本仓库核心错误处理体系内）；也没有全局 panic/recover 机制（Python 无此概念）。上述模式覆盖了后端运行时、HTTP 服务、流水线编排与外部 API 适配的主要错误处理面。