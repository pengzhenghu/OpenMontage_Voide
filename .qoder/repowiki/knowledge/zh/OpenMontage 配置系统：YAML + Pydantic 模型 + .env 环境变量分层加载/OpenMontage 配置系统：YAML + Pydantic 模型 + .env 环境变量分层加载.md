---
kind: configuration_system
name: OpenMontage 配置系统：YAML + Pydantic 模型 + .env 环境变量分层加载
category: configuration_system
scope:
    - '**'
source_files:
    - config.yaml
    - lib/config_model.py
    - lib/env_loader.py
    - .env.example
    - tools/cost_tracker.py
    - lib/paths.py
    - setup.py
---

## 1. 整体方案

OpenMontage 采用 **三层配置叠加** 的方式管理运行时配置：
- **顶层 YAML 配置文件** `config.yaml`：声明式定义 LLM、预算、检查点、输出参数与路径等全局设置。
- **Pydantic 数据模型** `lib/config_model.py`：用 Pydantic v2 的 `BaseModel` 对 `config.yaml` 进行强类型校验，并提供 `OpenMontageConfig.load()` 统一入口。
- **环境变量** `.env`（由 `lib/env_loader.py` 通过 `python-dotenv` 加载）：用于注入第三方 API Key、端点、本地路径等敏感或环境相关配置。

项目依赖在 `setup.py` 中显式声明了 `pyyaml>=6.0`、`pydantic>=2.0`、`python-dotenv>=1.0`，构成配置系统的核心依赖三角。

## 2. 关键文件与职责

| 文件 | 职责 |
|---|---|
| `config.yaml` | 全局运行期配置：`llm.*`、`budget.*`、`checkpoint.*`、`output.*`、`paths.*` |
| `lib/config_model.py` | 定义 `LLMConfig`、`BudgetConfig`、`CheckpointConfig`、`OutputConfig`、`PathsConfig`、`OpenMontageConfig` 等 Pydantic 模型；提供 `load()` 从 `config.yaml` 解析并校验；提供 `resolve_path(key, project_root)` 将相对路径解析为绝对路径 |
| `lib/env_loader.py` | 提供 `load_env(project_root)` 加载根目录 `.env`；`get_env(key, default)` 安全取值；`require_env(key)` 强制要求某变量存在，缺失时抛 `EnvironmentError` |
| `.env.example` | 文档化所有支持的第三方密钥与环境变量（FAL、Kling、Google、OpenAI、ElevenLabs、DashScope、Tencent、Suno、HeyGen、Runway、Volcengine、Pexels/Pixabay/Unsplash、Azure Speech、ComfyUI 等），测试会断言其每个 key 均为空值 |
| `tools/cost_tracker.py` | 消费 `BudgetMode` 枚举实现预算治理（observe/warn/cap 三模式、预留 reserve_pct、单动作审批阈值、新付费工具审批） |
| `lib/paths.py` | 使用 `OPENMONTAGE_PROJECTS_DIR` 环境变量覆盖默认项目目录 |
| `backlot/__main__.py` | 使用 `BACKLOT_PORT` 环境变量覆盖服务端口 |

## 3. 架构与设计约定

### 3.1 加载顺序
1. 进程启动时调用 `lib.env_loader.load_env()` 将 `.env` 载入 `os.environ`。
2. 业务模块按需调用 `OpenMontageConfig.load()` 读取 `config.yaml`，由 Pydantic 做字段类型校验与默认值填充。
3. 各工具/供应商通过 `os.environ.get(...)` 或 `lib.env_loader.require_env(...)` 直接读取环境变量获取密钥。

注意：当前实现中 `OpenMontageConfig.load()` **并未合并环境变量到 Pydantic 模型**——YAML 与 .env 是两套独立来源，YAML 负责“应用行为开关”，.env 负责“外部凭据”。

### 3.2 类型与枚举约束
- `BudgetMode`：`observe | warn | cap`，控制预算超支时的行为。
- `CheckpointPolicy`：`guided | manual_all | auto_noncreative`，控制检查点策略。
- 所有配置字段都有默认值，`config.yaml` 缺失时 `OpenMontageConfig.load()` 返回全默认实例，不会崩溃。

### 3.3 路径解析约定
`PathsConfig` 中的 `pipeline_dir`、`library_dir`、`styles_dir`、`skills_dir`、`output_dir` 均为相对于 `project_root` 的相对路径，通过 `OpenMontageConfig.resolve_path(key, project_root)` 解析。这使同一份 `config.yaml` 可在不同项目目录下复用。

### 3.4 预算治理作为配置驱动的行为
`tools/cost_tracker.py` 完全基于 `BudgetConfig` 中的 `mode`、`total_usd`、`reserve_pct`、`single_action_approval_usd`、`require_approval_for_new_paid_tool` 五个字段驱动：
- `cap` 模式：超出可用预算时抛 `BudgetExceededError`。
- `warn` 模式：记录 `budget_warning` 标记但不阻断。
- `single_action_approval_usd`：单次操作超过阈值抛 `ApprovalRequiredError`。
- `require_approval_for_new_paid_tool`：首次使用某个付费工具需人工批准。

## 4. 约定与约束

- **`.env` 必须通过 `load_env()` 显式加载**：测试 `tests/contracts/test_comfyui_tools.py` 断言未加载 `.env` 时会提示错误信息包含 `.env`，表明代码期望开发者主动调用 `load_env()`。
- **`.env.example` 是契约**：`tests/contracts/test_env_example.py` 使用 `dotenv_values(.env.example)` 断言每个文档化的 key 当前值为空，确保示例文件与实际支持的环境变量保持同步。
- **必需环境变量使用 `require_env`**：对于必须存在的密钥（如某些工具的 API Key），应通过 `lib.env_loader.require_env(key)` 获取，缺失时抛出明确的 `EnvironmentError`。
- **可选环境变量使用 `get_env`**：非关键配置通过 `lib.env_loader.get_env(key, default)` 获取，避免硬编码默认值散落各处。
- **YAML 配置变更受 Pydantic 校验**：新增字段需在 `OpenMontageConfig` 对应子模型中添加，否则 `model_validate` 会拒绝未知字段。
- **路径一律通过 `resolve_path` 解析**：禁止在业务代码中拼接 `config.paths.xxx` 字符串，统一走 `OpenMontageConfig.resolve_path` 以正确处理相对路径与 `project_root`。
- **项目级覆盖**：`OPENMONTAGE_PROJECTS_DIR` 环境变量可覆盖默认项目目录（见 `lib/paths.py`），脚本可通过 `os.environ[...]` 临时覆盖（如 `scripts/backlot_screenshot_stage.py`）。

## 5. 适用性说明

该配置系统适用于 OpenMontage 平台的所有子模块（Backlot、Ink Theater、Remotion Composer、工具注册中心、核心运行时、Schema、流水线定义、样式/技能知识库、测试套件），因为它们共享同一套 `lib/config_model.py` 与 `lib/env_loader.py` 提供的配置基础设施。