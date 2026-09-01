---
kind: build_system
name: OpenMontage 构建系统：Makefile + pip/requirements + Remotion/npm + GitHub Actions CI
category: build_system
scope:
    - '**'
source_files:
    - Makefile
    - setup.py
    - requirements.txt
    - requirements-dev.txt
    - requirements-gpu.txt
    - .github/workflows/ci.yml
    - render-demo.sh
    - render_demo.py
    - .env.example
---

## 1. 使用的构建系统与工具

OpenMontage 采用 **Python 包 + Node.js 子工程** 的混合构建模式，通过根级 `Makefile` 统一编排所有安装、测试与演示任务。

- **Python 环境管理**：默认 Python 3.10（可通过 `PYTHON_VERSION` 覆盖），优先使用 `uv venv`，回退到 `python -m venv`；支持激活的 virtualenv / conda 环境自动检测。
- **依赖管理**：三层 requirements 文件——`requirements.txt`（核心运行时）、`requirements-dev.txt`（开发/测试）、`requirements-gpu.txt`（GPU 加速依赖）。
- **Python 打包**：`setup.py` 使用 setuptools 定义 `openmontage` 包，版本硬编码为 `0.1.0`，声明 `python_requires=">=3.10"`。
- **Node.js 子工程**：`remotion-composer/` 是独立的 npm 项目，通过 `make setup` 中的 `cd remotion-composer && npm install` 安装。
- **外部二进制依赖**：CI 中通过 `apt-get install ffmpeg` 安装 FFmpeg；HyperFrames 渲染依赖 node/npx/ffmpeg。
- **CI**：GitHub Actions `.github/workflows/ci.yml`，在 `main` 分支 push/PR 时触发，使用 Ubuntu + Python 3.11。

## 2. 关键文件

| 文件 | 作用 |
|---|---|
| `Makefile` | 全部构建入口：venv 创建、依赖安装、测试、demo、lint、clean |
| `setup.py` | Python 包元数据与基础依赖声明 |
| `requirements.txt` | 生产依赖（pyyaml、pydantic、jsonschema、fastapi、uvicorn 等） |
| `requirements-dev.txt` | 测试/开发依赖 |
| `requirements-gpu.txt` | GPU 加速依赖（diffusers/transformers/accelerate） |
| `.github/workflows/ci.yml` | GitHub Actions 流水线 |
| `render-demo.sh` | 零键值 demo 渲染脚本入口 |
| `render_demo.py` | 调用 `npx remotion render` 渲染 Remotion 示例视频 |
| `config.yaml` | 运行时配置（由 Makefile setup 阶段从 `.env.example` 复制生成 `.env`） |
| `remotion-composer/package.json` | Remotion Composer 的 npm 依赖与构建脚本 |

## 3. 架构与约定

### 3.1 单点入口 `make`
`Makefile` 将所有操作收敛为单一命令：
- `make setup`：创建 venv → 安装 Python 依赖 → `npm install` → 安装 Piper TTS → 预热 HyperFrames npx 缓存 → 复制 `.env.example` → 打印提示。
- `make install` / `make install-dev` / `make install-gpu`：按场景安装不同依赖集。
- `make test`：运行 `pytest tests/ -v`。
- `make test-contracts`：仅运行契约测试 `tests/contracts/`。
- `make hyperframes-doctor`：通过 `HyperFramesCompose().execute({'operation':'doctor'})` 探测 node/ffmpeg/npx/HyperFrames 运行时。
- `make hyperframes-warm`：`npx --yes --prefer-online hyperframes --version` 刷新 npx 缓存。
- `make demo` / `make demo-list`：调用 `render_demo.py` 渲染 Remotion 示例。
- `make lint`：对 `base_tool.py`、`tool_registry.py`、`cost_tracker.py`、`composition_validator.py` 做 `py_compile` 语法检查。
- `make clean`：递归删除 `__pycache__` 和 `*.pyc`（跳过 venv 目录）。

### 3.2 虚拟环境发现策略
`RUN_PYTHON` 变量按顺序查找：`$VIRTUAL_ENV` → `$CONDA_PREFIX` → `./.venv/bin/python`（或 Windows `Scripts/python.exe`）。若均不存在且 `uv` 可用则用 `uv venv --python 3.10` 创建，否则回退到 `python -m venv`。创建后强制校验 Python 版本 ≥ 目标版本。

### 3.3 多依赖层
- 核心依赖集中在 `requirements.txt`，包含 OpenAI、Google GenAI、FastAPI、Uvicorn、Watchfiles 等。
- GPU 依赖通过 `make install-gpu` 单独安装 `diffusers transformers accelerate`，避免 CPU 环境被污染。
- 开发依赖通过 `requirements-dev.txt` 隔离。

### 3.4 Node.js 集成
Remotion Composer 作为独立 npm 子工程，通过 `make setup` 中的 `cd remotion-composer && npm install` 安装依赖。`render_demo.py` 在运行时自动检测 `node/npm/npx`，若 `node_modules` 不存在则执行 `npm install`，然后调用 `npx remotion render src/index.tsx Explainer <output> --props <demo>.json --codec h264`。

### 3.5 CI 流水线
`.github/workflows/ci.yml`：
- 触发条件：push/PR to `main`。
- 并发控制：`ci-${{ github.workflow }}-${{ github.ref }}` 组，取消进行中任务。
- 步骤：checkout → setup-python@v5 (3.11, 缓存 pip) → `apt-get install ffmpeg` → `make install-dev` → `make lint` → `make test`。
- 权限：仅 `contents: read`。

## 4. 约定与约束

- **Python 版本要求**：`setup.py` 声明 `python_requires=">=3.10"`，`Makefile` 默认 `PYTHON_VERSION=3.10`，CI 使用 3.11；`ensure-venv` 会显式校验当前解释器版本并拒绝不兼容环境。
- **FFmpeg 为必需系统依赖**：CI 通过 apt 安装；本地 HyperFrames/Remotion 渲染也依赖它，未安装时会失败。
- **环境变量通过 `.env` 注入**：`make setup` 自动从 `.env.example` 复制生成 `.env`，供 python-dotenv 加载 API Key。
- **测试网络隔离**：测试套件通过 socket 拦截禁止访问真实网络（见 `tests/test_network_guard.py`），确保单元测试可离线运行。
- **无 Dockerfile**：仓库未提供容器化构建，部署依赖宿主机安装 Python + Node + FFmpeg。
- **版本号硬编码**：`setup.py` 中 `version="0.1.0"` 为静态字符串，未见自动化版本 bump 流程。
- **发布产物**：目前仅通过 `pip install .` 安装 Python 包；Remotion 子工程通过 npm 独立管理，未见统一的 npm publish 流程。
- **清理约定**：`make clean` 明确排除 `./.venv` 和 `./venv` 目录，避免误删虚拟环境。