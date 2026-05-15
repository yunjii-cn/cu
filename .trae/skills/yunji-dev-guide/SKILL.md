---
name: "yunji-dev-guide"
description: "云集智能文件清理专家项目开发规范。Invoke when working on this project: coding, building EXE, modifying UI, fixing bugs, or any development task."
---

# 云集智能文件清理专家 - 开发规范技能

## 项目核心信息

- **项目名称**: 云集智能文件清理专家
- **GUI框架**: CustomTkinter (基于Tkinter)
- **打包工具**: PyInstaller (`--onedir` 模式，**禁止** `--onefile`)
- **源代码目录**: `dev/app/`
- **构建脚本**: `build/build.py`
- **EXE输出位置**: `dev/云集智能文件清理专家.exe` + `dev/_internal/`

## 必须遵守的规则

### 1. EXE输出位置
- **EXE必须直接输出到 `dev/` 目录下**，即 `dev/云集智能文件清理专家.exe` 和 `dev/_internal/`
- **禁止**将EXE输出到版本号子目录、项目根目录、build目录或其他位置
- 构建脚本 `build/build.py` 已配置为自动将产物复制到 `dev/` 目录

### 2. 构建流程
- 构建命令: `python build/build.py`（从项目根目录运行）
- **构建前必须测试**: `python -c "import sys; sys.path.insert(0, 'dev/app'); import main"` 确保代码能正常加载
- 必须使用 `--onedir` 模式（`--onefile` 会导致 Conda DLL 加载失败）
- 每次构建会覆盖 `dev/` 下的旧版EXE和 `_internal/`

### 3. CustomTkinter 注意事项
- `CTkScrollbar` 不支持 `scrollbar_color`/`scrollbar_hover_color`，应使用 `button_color`/`button_hover_color`
- 构建前务必验证所有CTk组件参数是否支持，避免EXE启动崩溃
- 不要使用CTk文档中未列出的参数

### 4. Git管理范围
- **提交**: 只提交 `dev/app/` 和 `docs/` 的源代码
- **不提交**: EXE文件、`_internal/`、`build/` 目录
- **gitignore**: `*.exe` 和 `_internal/` 已配置忽略

### 5. 版本号管理
- 版本号格式: `YYYY.MM.DD.HHMM`（如 `2026.05.16.0105`）
- 构建脚本自动注入版本号到 `main.py` 的 `VERSION` 变量
- 构建完成后自动恢复为 `DEV`
- 版本信息自动更新到 `version_history.json` 和 `dev/ver/version.json`

### 6. 性能规范
- 文件校验（`os.path.exists`/`os.stat`）必须在后台线程执行，禁止在主线程阻塞
- 自动保存结果使用节流机制（间隔≥5秒），不要每批次都保存
- 使用缓存字典（如 `_file_size_map`）避免每次遍历全量数据
- Treeview批量更新，减少逐行操作

### 7. UI设计规范
- 暗黑卡片式设计风格
- 分类标签使用grid布局：一级分类row0，二级分类展开row1
- 调色按钮灰色（`#444`），放在标签外部右侧
- 分类间距 `padx=10`（合计20px间隔）
- 功能设置按钮间距 `padx=10`（合计20px间隔）
- 面板管理使用 `_current_panel`/`_current_panel_type` 统一跟踪，不用 `pack_forget`/`pack` 切换

## 目录结构

```
云集智能文件清理专家/
├── docs/                        # 文档 (Git管理)
│   └── 开发指南.md
├── .gitignore                   # Git忽略配置
├── dev/
│   ├── 云集智能文件清理专家.exe  # ❌ EXE (gitignore)
│   ├── _internal/               # ❌ PyInstaller运行时 (gitignore)
│   ├── app/                     # ✅ 源代码 (Git管理)
│   │   ├── main.py              # 主程序
│   │   ├── launcher.py          # EXE入口点
│   │   ├── icon.ico/png         # 图标
│   │   ├── requirements.txt     # 依赖
│   │   └── version_history.json # 版本历史
│   └── ver/
│       └── version.json         # 版本信息 (gitignore)
└── build/                       # 构建历史 (gitignore)
    └── vYYYY.MM.DD.HHMM/
```

## 常见陷阱

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| EXE启动报DLL load failed | 使用了`--onefile`模式 | 必须用`--onedir` |
| EXE启动报ValueError不支持的参数 | CTk组件参数错误 | 构建前用import测试 |
| 扫描时UI假死 | 主线程执行IO操作 | 移至后台线程 |
| 面板无法展开/收回 | pack_forget/pack布局问题 | 使用destroy/recreate |
| 分类展开时宽度偏移 | grid列宽未固定 | 设置minsize |
