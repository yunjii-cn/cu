@echo off
chcp 65001 >nul 2>&1
title 云集智能文件清理专家 - 开发模式

set "PYTHON=%~dp0..\build\venv_new\Scripts\python.exe"
set "APP_DIR=%~dp0app"

if not exist "%PYTHON%" (
    echo [错误] 未找到构建环境: %PYTHON%
    echo 请先运行以下命令初始化构建环境:
    echo   python -m venv build\venv_new
    echo   build\venv_new\Scripts\pip.exe install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple customtkinter
    echo.
    pause
    exit /b 1
)

echo ══════════════════════════════════════════════════════
echo   云集智能文件清理专家 - 开发模式
echo ══════════════════════════════════════════════════════
echo.
echo Python: %PYTHON%
echo APP_DIR: %APP_DIR%
echo.

"%PYTHON%" -c "import sys; sys.path.insert(0, r'%APP_DIR%'); import main; main.main()"

if errorlevel 1 (
    echo.
    echo [失败] 程序异常退出，错误码: %errorlevel%
    pause
)
