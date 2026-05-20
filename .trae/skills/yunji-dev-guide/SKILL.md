---
name: "yunji-dev-guide"
description: "云集智能文件清理专家项目开发规范。Invoke when working on this project: coding, building EXE, modifying UI, fixing bugs, or any development task."
---

# 云集智能文件清理专家 - 开发规范技能

## 项目概述

**项目名称**: 云集智能文件清理专家
**核心功能**:
- 智能文件扫描与分类（按类型/大小/时间/重复文件）
- 文件类型自定义颜色标记
- 重复文件检测与批量留存策略
- 预设规则包（7种社区成熟清理规则）
- 分析报告（饼状图+统计+建议方案）
- 文件批量删除/移动/导出
- 软件版本管理与硬链接切换

## 目录结构

```
云集智能文件清理专家/
│
│ # ========== 公开仓库（Git管理） ==========
├── README.md                   # 项目说明（公开）
├── LICENSE                     # GPL-3.0 协议（公开）
├── docs/                       # 文档（公开）
│   ├── 开发指南.md
│   └── 用户使用说明.md
├── ver/                        # 版本信息（公开）
│   └── version.json            # 版本元数据（不含EXE）
├── .gitignore                  # Git忽略配置
│
│ # ========== 私有（Git不管理，仅本地） ==========
├── dev/                        # 应用安装根目录
│   ├── .yunji.lock             # 路径定位标记
│   ├── 云集智能文件清理专家.exe  # 统一入口（硬链接 → ver/）
│   ├── 运行.bat                # 开发调试启动脚本
│   ├── ver/                    # 本地版本仓库
│   │   └── *-vYYYY.MM.DD.HHMM.exe
│   └── app/                    # 核心源码（私有，不上传仓库）
│       ├── main.py             # 主程序
│       ├── launcher.py         # 入口文件
│       ├── downloader.py       # 下载器（独立精简EXE）
│       ├── icon.ico / icon.png # 应用图标
│       ├── requirements.txt    # Python依赖
│       ├── version_info.txt    # Windows版本信息
│       ├── version_history.json# 版本历史
│       ├── .gitee_token        # Gitee令牌（不入Git）
│       └── .github_token       # GitHub令牌（不入Git）
│
│ # ========== 构建相关（Git不管理） ==========
├── build/                      # 构建目录（按版本组织）
│   ├── build.py                # 构建脚本
│   ├── release.py              # 全自动发布脚本
│   ├── venv_new/               # 构建用虚拟环境（Python 3.12）
│   └── vYYYY.MM.DD.HHMM/      # 版本构建记录
│       ├── build.py            # 该版本构建脚本备份
│       ├── build/              # PyInstaller临时文件
│       └── dist/               # PyInstaller输出
│
│ # ========== 一键脚本 ==========
├── 打包.bat                    # 一键构建打包
└── 发布.bat                    # 一键发布到 GitHub + Gitee
```

## 完整开发→打包→分发流程

### 三步流程

```
┌─────────────────────────────────────────────────────────┐
│  1. 开发阶段                                             │
│     编辑 dev/app/main.py                                 │
│     双击 dev/运行.bat → 测试界面和功能                     │
│     （Python源码直接运行，改了代码立刻生效）                 │
│                                                          │
│     ⚠️ 发布前必做：更新 dev/app/version_history.json      │
│     写入本版本的更新内容（changes列表），否则Release无描述  │
└──────────────────────┬──────────────────────────────────┘
                       │ 功能OK + 版本描述已写
                       ▼
┌─────────────────────────────────────────────────────────┐
│  2. 打包阶段                                             │
│     双击 打包.bat 或 python build/build.py               │
│     → EXE输出到 dev/ver/云集智能文件清理专家-v版本号.exe    │
│     → 创建硬链接 dev/云集智能文件清理专家.exe → ver中的EXE  │
└──────────────────────┬──────────────────────────────────┘
                       │ 双击 dev/云集智能文件清理专家.exe 测试
                       │ 确认稳定
                       ▼
┌─────────────────────────────────────────────────────────┐
│  3. 发布阶段（全自动）                                    │
│     双击 发布.bat 或 python build/release.py              │
│     → 收集变更描述 → 构建 → 更新version.json → git push   │
│     → 创建GitHub Release + 上传EXE                       │
│     → 创建Gitee Release + 上传EXE                        │
│     → 用户通过软件更新页面即可检测下载                      │
└─────────────────────────────────────────────────────────┘
```

### 全自动发布脚本 (release.py)

一条命令完成从构建到发布的全流程：

```bash
python build/release.py
```

**7步自动流程**：

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1/7 | 收集变更描述 | 自动从version_history.json读取，支持编辑 |
| 2/7 | 构建EXE | 调用build.py |
| 3/7 | 获取版本信息 | 版本号、文件大小、更新内容 |
| 4/7 | 更新version.json | 更新latest和versions列表 |
| 5/7 | Git提交并推送 | 推送到GitHub + Gitee |
| 6/7 | 创建GitHub Release | 上传EXE（无空间限制） |
| 7/7 | 创建Gitee Release | 上传EXE（1GB空间限制） |

### 分发策略

| 平台 | 上传内容 | 原因 |
|------|---------|------|
| **GitHub** | EXE | 公开仓库无空间限制 |
| **Gitee** | EXE | 1GB空间限制，国内直连 |

| 用户场景 | 下载方式 | 说明 |
|---------|---------|------|
| 新用户安装 | Release EXE | 双击→自部署→自动创建目录结构 |
| 老用户更新 | 软件内更新 | 只下载新EXE到ver/，硬链接切换 |

## EXE自部署机制

EXE首次运行时自动检测环境，无需额外安装器：

```
EXE启动
  │
  ├─ 发现 .yunji.lock 或 app/ 目录？
  │   ├─ 是 → 正常运行（已有环境）
  │   └─ 否 → 首次运行，执行自部署：
  │            1. 在EXE同级目录创建 云集智能文件清理专家/ 文件夹
  │            2. 创建 ver/ 和 app/ 子目录
  │            3. 创建 .yunji.lock 标记文件
  │            4. 将自己复制到 ver/ 并按版本号命名
  │            5. 创建硬链接入口 云集智能文件清理专家.exe
  │            6. 继续正常启动
  │
  └─ 之后双击入口EXE → 硬链接指向ver/中的EXE → 正常运行
```

**关键代码**：`_self_deploy()` 函数在 `_find_dev_dir()` 中被调用，当EXE在非标准目录运行时自动触发。

## 版本管理与硬链接机制

### 硬链接方案

版本切换采用硬链接映射，而非复制替换：

```
dev/
├── 云集智能文件清理专家.exe          ← 硬链接入口（始终指向当前版本）
└── ver/
    ├── 云集智能文件清理专家-v2026.05.18.0630.exe
    └── 云集智能文件清理专家-v2026.05.20.2052.exe  ← 入口硬链接指向此文件
```

**工作原理**：
- `云集智能文件清理专家.exe` 是 `ver/` 中某个版本EXE的硬链接
- 切换版本 = 删除旧硬链接 + 创建新硬链接（瞬间完成，无需复制文件）
- 硬链接与原文件共享同一磁盘数据，不占额外空间

### 路径解析机制

`_find_dev_dir()` 从 EXE 所在目录向上搜索 `.yunji.lock` 或 `app/` 目录来定位 `dev/`：

| 运行方式 | sys.executable | 解析结果 |
|---------|---------------|---------|
| `dev/云集智能文件清理专家.exe` | `dev/` | 直接找到 `.yunji.lock` → `dev/` |
| `dev/ver/*-v2026.xx.xx.xxxx.exe` | `dev/ver/` | 向上一层 → `dev/` |
| 任意目录首次运行 | 任意目录 | 触发 `_self_deploy()` → 自动部署 |
| `python main.py` | - | 从 `__file__` 推算 → `dev/` |

### 版本切换流程

1. 用户点击「切换」按钮
2. 程序生成 `_switch_version.bat` 批处理脚本
3. 批处理等待当前进程退出（最多30秒）
4. 删除旧入口硬链接
5. 创建新硬链接指向目标版本
6. 启动新版本EXE
7. 删除批处理脚本自身

### 应用内下载

- 远程版本通过 GitHub/Gitee Releases 分发
- 竞速下载机制：Gitee + GitHub加速代理 + GitHub直连，哪个先返回用哪个
- 下载到 `dev/ver/` 目录，支持进度显示
- 下载完成后询问是否立即切换

## Git管理范围

| 目录 | Git管理 | 公开 | 说明 |
|------|---------|------|------|
| **README.md** | ✅ | ✅ | 项目说明 |
| **LICENSE** | ✅ | ✅ | GPL-3.0协议 |
| **docs/** | ✅ | ✅ | 开发文档 |
| **ver/version.json** | ✅ | ✅ | 版本元数据 |
| **dev/app/** | ✅ | ✅ | 核心源码，GPL-3.0协议要求公开 |
| **dev/ver/*.exe** | ❌ | ❌ | EXE文件，通过Release分发 |
| **build/** | ❌ | ❌ | 构建目录 |

## 开源策略与版权保护

### 协议选择：GPL-3.0

本项目采用 GPL-3.0 协议，核心约束：

- ✅ 允许自由使用、修改和分发
- ❌ **禁止闭源商业使用** — 任何衍生作品必须同样以 GPL-3.0 开源
- ❌ **禁止移除版权声明**

### 双仓库架构

| 仓库 | 平台 | 可见性 | 内容 | 角色 |
|------|------|--------|------|------|
| **GitHub** | github.com/yunjii-cn/cu | 公开 | README、LICENSE、docs、ver/version.json | **主仓库** |
| **Gitee** | gitee.com/yunjii/cu | 公开 | 与GitHub同步，国内直连 | **国内镜像** |

**工作方式**：
- 只需推送到 GitHub，Gitee 通过内置镜像功能自动同步
- Gitee 镜像设置：Gitee 仓库 → 管理 → 镜像管理 → 从 GitHub 导入

### 分层公开策略

| 内容 | 公开方式 | 说明 |
|------|---------|------|
| README.md / LICENSE | GitHub 仓库公开 | 项目介绍和协议 |
| ver/version.json | GitHub 仓库公开 | 版本元数据（供软件更新检查） |
| docs/ | GitHub 仓库公开 | 开发文档 |
| EXE文件 | GitHub/Gitee Releases | 用户下载，非仓库存储 |
| dev/app/ 源码 | GitHub/Gitee 仓库公开 | 核心代码，GPL-3.0协议要求公开 |
| build/ 构建脚本 | **不公开** | 构建工具仅本地保留 |

### 软件更新双源机制

软件检查更新时并行请求两个源，谁先返回用谁（自动适应网络环境）：

| 优先级 | 来源 | URL方式 | 需要Token | 说明 |
|--------|------|---------|-----------|------|
| 并行 | Gitee | `gitee.com/yunjii/cu/raw/main/ver/version.json` | ❌（公开仓库） | 国内直连 |
| 并行 | GitHub | `raw.githubusercontent.com/yunjii-cn/cu/main/ver/version.json` | ❌ | 需代理 |

下载EXE时采用竞速机制：Gitee + GitHub加速代理(ghfast.top/gh-proxy.com/ghproxy.cc) + GitHub直连，哪个先返回用哪个。

### 令牌管理

令牌不硬编码在源码中，从配置文件读取（配置文件不入Git）：

| 文件 | 用途 | 位置 |
|------|------|------|
| `.gitee_token` | Gitee仓库访问令牌 | `dev/app/.gitee_token` |
| `.github_token` | GitHub API令牌 | `dev/app/.github_token` |

**安全提醒**：源码中不得硬编码任何令牌或密钥。

## 核心文件说明

### 应用目录 (`dev/app/`)

| 文件 | 用途 | 说明 |
|------|------|------|
| `main.py` | 主程序 | CustomTkinter GUI，文件清理核心，含自部署逻辑 |
| `launcher.py` | 入口文件 | 杀旧进程 + 调用 main.py |
| `downloader.py` | 下载器 | 独立精简EXE，用于版本下载 |
| `icon.ico` | 应用图标 | Windows图标 |
| `icon.png` | 高清图标 | PNG格式图标 |
| `requirements.txt` | Python依赖 | customtkinter, psutil, Pillow等 |
| `version_history.json` | 版本历史 | 构建记录 |
| `version_info.txt` | 版本信息 | Windows文件属性（构建时自动更新） |

### 构建脚本 (`build/build.py`)

**构建命令**：
```bash
python build/build.py
```

**构建流程**：
1. 动态生成版本号：`YYYY.MM.DD.HHMM`
2. 将版本号注入 `dev/app/main.py` 和 `version_info.txt`
3. PyInstaller 从 `launcher.py` 构建 EXE（`--onefile` 模式）
4. EXE 移动到 `dev/ver/` 目录
5. 在 `dev/` 创建硬链接入口 `云集智能文件清理专家.exe`
6. 构建完成后恢复源代码中的版本号

**构建下载器**：
```bash
python build/build.py downloader
```
构建独立精简版下载器EXE，排除CustomTkinter等大型依赖。

### 开发启动脚本 (`dev/运行.bat`)

双击即可运行 Python 源码进行开发调试，无需命令行。

## 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.12+ | 开发语言 |
| CustomTkinter | GUI框架（基于Tkinter） |
| Pillow | 图标/图像处理 |
| psutil | 系统信息 |
| PyInstaller | EXE打包 |
| Windows硬链接 | 版本切换（mklink /H） |
| GitHub Releases | 版本分发（主） |
| Gitee Releases | 版本分发（备用） |
| Gitee API v5 | 远程版本信息获取 |
| concurrent.futures | 竞速下载 |

## 开发规范指令

When working on this project, follow these rules:

### 代码修改规范
- 所有核心源码位于 `dev/app/` 目录，修改代码时只操作此目录
- 主程序入口为 `launcher.py`（杀旧进程），核心逻辑在 `main.py`
- GUI 基于 CustomTkinter，遵循 CustomTkinter 的组件参数规范
- 代码中不得硬编码任何令牌或密钥，从配置文件读取

### 构建规范
- 构建命令：`python build/build.py`
- 版本号格式：`YYYY.MM.DD.HHMM`，由构建脚本动态生成
- 构建完成后源码中的版本号会被恢复，不要手动修改版本号
- EXE 输出到 `dev/ver/` 目录，硬链接入口在 `dev/` 目录
- **构建前必须测试**: `python -c "import sys; sys.path.insert(0, 'dev/app'); import main"` 确保代码能正常加载
- CustomTkinter 的 CTkScrollbar 不支持 `scrollbar_color`/`scrollbar_hover_color`，应使用 `button_color`/`button_hover_color`

### 发布规范
- 发布命令：`python build/release.py`（全自动，一条命令完成构建+发布）
- GitHub Release 上传 EXE（无空间限制）
- Gitee Release 上传 EXE（1GB空间限制，自动清理旧版本）
- 发布前确保 `dev/app/.gitee_token` 和 `dev/app/.github_token` 已配置
- **版本描述是必填流程**：发布前必须更新 `dev/app/version_history.json`，添加版本号、日期和变更列表
  - release.py 会自动读取 version_history.json 作为 Release 描述
  - 如果 version_history.json 中没有当前版本的记录，Release 将无描述
  - 格式：`{"version": "2026.05.20.2052", "date": "2026-05-20", "changes": ["修复XX问题", "新增XX功能"]}`

### Git提交规范
- 只提交公开文件：`README.md`、`docs/`、`ver/version.json`
- 不提交私有文件：`dev/app/`、`build/`、`dev/ver/*.exe`
- 提交信息格式：`v版本号: 修改描述`
- 推送到 GitHub，Gitee 自动镜像

### 版本切换规范
- 版本切换使用 Windows 硬链接（mklink /H），不使用文件复制
- 路径定位依赖 `.yunji.lock` 标记文件，不要删除此文件
- 版本切换通过新EXE启动后自动完成（利用 `_kill_old_instances()` 机制）
- 切换流程：新EXE启动 → 杀旧进程 → 删除旧硬链接 → 创建新硬链接 → 删除原始下载文件（通过 `--cleanup` 参数）

### 关于弹窗规范
- 关于信息通过弹窗展示，不单独作为导航栏目
- 入口按钮位于软件更新页面的顶部工具栏左侧
- **弹窗内容必须与 README.md 保持同步**，修改 README 时同步修改关于弹窗，反之亦然
- 弹窗内容结构：软件名称 → 标语 → 版本号 → 描述 → 功能亮点 → 开源协议与版权 → 链接（GitHub / Gitee / 问题反馈）

### 自部署规范
- EXE首次运行时自动检测环境，无需安装器
- `_self_deploy()` 函数负责创建目录结构和硬链接入口
- 自部署后EXE在 `ver/` 目录中，入口硬链接在部署根目录

### 安全规范
- 令牌文件（`.gitee_token`、`.github_token`）不入 Git
- 源码中不得硬编码任何令牌或密钥
- 遵守 GPL-3.0 协议，禁止闭源商业使用，禁止移除版权声明

### 性能规范
- 文件校验（`os.path.exists`/`os.stat`）必须在后台线程执行，禁止在主线程阻塞
- 自动保存结果使用节流机制（间隔≥5秒），不要每批次都保存
- 使用缓存字典（如 `_file_size_map`）避免每次遍历全量数据
- Treeview批量更新，减少逐行操作

### UI设计规范
- 暗黑卡片式设计风格
- 分类标签使用grid布局：一级分类row0，二级分类展开在row1同一列
- 二级分类dropdown背景透明（`#1e1e1e`），只有tag_frame有背景色
- 二级分类与一级分类总宽度保持一致，展开后一级分类不偏移
- 调色按钮灰色（`#444`），放在标签外部右侧
- 分类间距 `padx=7`（合计14px间隔）
- 功能设置按钮间距 `padx=10`（合计20px间隔）
- 面板管理使用 `_current_panel`/`_current_panel_type` 统一跟踪，不用 `pack_forget`/`pack` 切换
- 启动时不自动恢复扫描结果，右下角"恢复进度"按钮提供手动恢复选项

## 常见陷阱

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| EXE启动报DLL load failed | DLL依赖未收集 | 使用build.py自动收集DLL |
| EXE启动报ValueError不支持的参数 | CTk组件参数错误 | 构建前用import测试 |
| 扫描时UI假死 | 主线程执行IO操作 | 移至后台线程 |
| 面板无法展开/收回 | pack_forget/pack布局问题 | 使用destroy/recreate |
| 分类展开时宽度偏移 | grid列宽未固定 | 设置minsize |
| 发布时令牌未配置 | .gitee_token/.github_token缺失 | 创建令牌文件 |
