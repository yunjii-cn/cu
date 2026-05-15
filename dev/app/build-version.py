import os
import sys
import re
import json
import shutil
import datetime
import subprocess

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DEV_DIR = os.path.dirname(APP_DIR)
ROOT_DIR = os.path.dirname(DEV_DIR)
BUILD_ROOT = os.path.join(ROOT_DIR, "build")
VER_DIR = os.path.join(DEV_DIR, "ver")
MAIN_PY = os.path.join(APP_DIR, "main.py")
VERSION_HISTORY = os.path.join(APP_DIR, "version_history.json")
VERSION_JSON = os.path.join(VER_DIR, "version.json")
ICON_FILE = os.path.join(APP_DIR, "icon.ico")
ICON_PNG = os.path.join(APP_DIR, "icon.png")
VERSION_INFO_FILE = os.path.join(APP_DIR, "version_info.txt")
LAUNCHER_PY = os.path.join(APP_DIR, "launcher.py")

APP_NAME = "云集智能文件清理专家"
VERSION_PATTERN = r'^VERSION\s*=\s*"[^"]*"'
VERSION_PLACEHOLDER = 'VERSION = "DEV"'


def _detect_python():
    venv_python = os.path.join(APP_DIR, ".venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        return venv_python

    conda_candidates = [
        os.path.join(os.environ.get("CONDA_PREFIX", ""), "python.exe"),
        r"C:\ProgramData\miniconda3\python.exe",
        r"C:\ProgramData\anaconda3\python.exe",
        os.path.join(os.environ.get("USERPROFILE", ""), "miniconda3", "python.exe"),
        os.path.join(os.environ.get("USERPROFILE", ""), "anaconda3", "python.exe"),
    ]
    for candidate in conda_candidates:
        if candidate and os.path.exists(candidate):
            return candidate

    return sys.executable


def _is_conda_python(python_exe):
    python_dir = os.path.dirname(python_exe)
    if os.path.exists(os.path.join(python_dir, "conda-meta")):
        return True
    parent = os.path.dirname(python_dir)
    if os.path.exists(os.path.join(parent, "conda-meta")):
        return True
    return False


def _find_conda_dlls(python_exe):
    python_dir = os.path.dirname(python_exe)
    if os.path.exists(os.path.join(python_dir, "conda-meta")):
        python_dir = os.path.dirname(python_dir)

    dll_dirs = []
    extra_dlls = []

    lib_bin = os.path.join(python_dir, "Library", "bin")
    dlls_dir = os.path.join(python_dir, "DLLs")

    if os.path.isdir(lib_bin):
        dll_dirs.append(lib_bin)
    if os.path.isdir(dlls_dir):
        dll_dirs.append(dlls_dir)

    bin_dll_names = [
        "ffi.dll", "ffi-7.dll", "ffi-8.dll",
        "tcl86t.dll", "tk86t.dll",
        "libcrypto-3-x64.dll", "libcrypto-3.dll",
        "libssl-3-x64.dll", "libssl-3.dll",
        "liblzma.dll", "libexpat.dll", "libbz2.dll",
        "sqlite3.dll", "zlib.dll", "zlib1.dll",
    ]
    for dll_name in bin_dll_names:
        for d in dll_dirs:
            dll_path = os.path.join(d, dll_name)
            if os.path.isfile(dll_path):
                extra_dlls.append(dll_path)
                break

    pyd_modules = [
        "_tkinter", "_ctypes", "_ssl", "_hashlib",
        "_lzma", "_bz2", "_sqlite3", "_decimal",
        "_elementtree", "_multiprocessing", "_overlapped",
        "_socket", "_queue", "_asyncio",
    ]
    for mod_name in pyd_modules:
        try:
            result = subprocess.run(
                [python_exe, "-c", f"import {mod_name}; print({mod_name}.__file__)"],
                capture_output=True, text=True, timeout=10
            )
            path = result.stdout.strip()
            if path and os.path.isfile(path) and path not in extra_dlls:
                extra_dlls.append(path)
        except Exception:
            pass

    tcl_dir = os.path.join(python_dir, "Library", "lib", "tcl8.6")
    tk_dir = os.path.join(python_dir, "Library", "lib", "tk8.6")
    if not os.path.isdir(tcl_dir):
        tcl_dir = os.path.join(python_dir, "tcl", "tcl8.6")
    if not os.path.isdir(tk_dir):
        tk_dir = os.path.join(python_dir, "tcl", "tk8.6")

    extra_dlls = list(dict.fromkeys(extra_dlls))
    return dll_dirs, extra_dlls, tcl_dir, tk_dir


def generate_version():
    now = datetime.datetime.now()
    return now.strftime("%Y.%m.%d.%H%M")


def inject_version(version):
    with open(MAIN_PY, "r", encoding="utf-8") as f:
        content = f.read()
    new_line = f'VERSION = "{version}"'
    content = re.sub(VERSION_PATTERN, new_line, content, count=1, flags=re.MULTILINE)
    with open(MAIN_PY, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[1/7] 版本号注入: {version}")


def restore_version():
    with open(MAIN_PY, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(VERSION_PATTERN, VERSION_PLACEHOLDER, content, count=1, flags=re.MULTILINE)
    with open(MAIN_PY, "w", encoding="utf-8") as f:
        f.write(content)
    print("[6/7] 版本号已恢复为 DEV")


def update_version_info(version):
    parts = version.split(".")
    while len(parts) < 4:
        parts.append("0")
    file_ver = tuple(int(p) for p in parts)

    content = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={file_ver},
    prodvers={file_ver},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0,0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'080404b0',
      [StringStruct(u'CompanyName', u'YunJi'),
      StringStruct(u'FileDescription', u'{APP_NAME}'),
      StringStruct(u'FileVersion', u'{version}'),
      StringStruct(u'InternalName', u'yunji_cleanup'),
      StringStruct(u'LegalCopyright', u'Copyright (C) 2026 YunJi'),
      StringStruct(u'OriginalFilename', u'{APP_NAME}.exe'),
      StringStruct(u'ProductName', u'{APP_NAME}'),
      StringStruct(u'ProductVersion', u'{version}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [2052, 1200])])
  ]
)
"""
    with open(VERSION_INFO_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[1.5/7] version_info.txt 已更新: {version}")


def build_exe(version):
    version_build_dir = os.path.join(BUILD_ROOT, f"v{version}")
    os.makedirs(version_build_dir, exist_ok=True)

    exe_name = f"{APP_NAME}-v{version}"
    python_exe = _detect_python()

    dist_dir = os.path.join(version_build_dir, "dist")
    work_dir = os.path.join(version_build_dir, "build")

    is_conda = _is_conda_python(python_exe)

    cmd = [
        python_exe, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        f"--name={APP_NAME}",
        f"--icon={ICON_FILE}",
        f"--version-file={VERSION_INFO_FILE}",
        f"--distpath={dist_dir}",
        f"--workpath={work_dir}",
        f"--specpath={version_build_dir}",
    ]

    if is_conda:
        dll_dirs, extra_dlls, tcl_dir, tk_dir = _find_conda_dlls(python_exe)

        for d in dll_dirs:
            cmd.append(f"--paths={d}")

        for dll_path in extra_dlls:
            cmd.append(f"--add-binary={dll_path};.")
            print(f"      添加DLL: {os.path.basename(dll_path)}")

        if os.path.isdir(tcl_dir):
            cmd.append(f"--add-data={tcl_dir};tcl/tcl8.6")
            print(f"      添加Tcl: {tcl_dir}")
        if os.path.isdir(tk_dir):
            cmd.append(f"--add-data={tk_dir};tk/tk8.6")
            print(f"      添加Tk: {tk_dir}")

        print(f"[2/7] 开始 PyInstaller 构建（onefile + Conda DLL收集）...")
        print(f"      Python: {python_exe} (Conda)")
        print(f"      额外DLL: {len(extra_dlls)} 个")

        env = os.environ.copy()
        if dll_dirs:
            env["PATH"] = os.pathsep.join(dll_dirs) + os.pathsep + env.get("PATH", "")
    else:
        print(f"[2/7] 开始 PyInstaller 构建（onefile模式）...")
        print(f"      Python: {python_exe}")
        env = None

    if os.path.isfile(ICON_FILE):
        cmd.append(f"--add-data={ICON_FILE};.")
    if os.path.isfile(ICON_PNG):
        cmd.append(f"--add-data={ICON_PNG};.")

    cmd.append(LAUNCHER_PY)

    print(f"      输出目录: {dist_dir}")

    result = subprocess.run(cmd, cwd=APP_DIR, env=env)
    if result.returncode != 0:
        print(f"❌ 构建失败! 退出码: {result.returncode}")
        sys.exit(1)

    built_exe = os.path.join(dist_dir, f"{APP_NAME}.exe")
    final_exe = os.path.join(DEV_DIR, f"{APP_NAME}-v{version}.exe")
    if os.path.exists(built_exe):
        shutil.copy2(built_exe, final_exe)
        print(f"[3/7] EXE已复制到: {final_exe}")
    else:
        print(f"❌ 构建产物未找到: {built_exe}")
        sys.exit(1)

    return final_exe, exe_name, version_build_dir


def cleanup_old_versions(current_exe_name):
    old_exes = [f for f in os.listdir(DEV_DIR)
                if f.startswith(APP_NAME + "-v") and f.endswith(".exe") and f != current_exe_name]
    if old_exes:
        print(f"[4/7] 保留 {len(old_exes)} 个旧版EXE（不删除）:")
        for f in sorted(old_exes):
            size_mb = os.path.getsize(os.path.join(DEV_DIR, f)) / (1024 * 1024)
            print(f"      - {f} ({size_mb:.1f}MB)")
    else:
        print("[4/7] 无旧版EXE")


def backup_build_script(version, version_build_dir):
    src = os.path.abspath(__file__)
    dst = os.path.join(version_build_dir, "build-version.py")
    shutil.copy2(src, dst)
    print(f"[5/7] 构建脚本已备份到: {dst}")


def update_version_history(version, dir_name, changes=None):
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    if not changes:
        changes = [f"版本 {version} 构建"]

    entry = {
        "version": version,
        "date": date_str,
        "exe": f"{dir_name}.exe",
        "changes": changes,
    }

    if os.path.exists(VERSION_HISTORY):
        with open(VERSION_HISTORY, "r", encoding="utf-8") as f:
            history = json.load(f)
    else:
        history = []

    history.insert(0, entry)

    with open(VERSION_HISTORY, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    print(f"[7/7] version_history.json 已更新")


def update_version_json(version, dir_name, changes=None):
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")

    if not changes:
        changes = [f"版本 {version} 构建"]

    entry = {
        "version": version,
        "date": date_str,
        "exe": f"{dir_name}.exe",
        "changes": changes,
    }

    if os.path.exists(VERSION_JSON):
        with open(VERSION_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"latest": "", "versions": []}

    data["latest"] = version
    existing = [v for v in data.get("versions", []) if v.get("version") != version]
    existing.insert(0, entry)
    data["versions"] = existing

    with open(VERSION_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[7.5/7] version.json 已更新")


def main():
    changes = sys.argv[1:] if len(sys.argv) > 1 else None

    print("=" * 60)
    print(f"  {APP_NAME} - 构建脚本")
    print("=" * 60)

    python_exe = _detect_python()
    is_conda = _is_conda_python(python_exe)
    print(f"\n📌 Python: {python_exe}")
    print(f"📌 环境: {'Conda (需DLL收集)' if is_conda else '标准Python'}")

    version = generate_version()
    print(f"📌 版本号: {version}")
    if changes:
        print(f"📌 修改内容: {', '.join(changes)}")
    print()

    inject_version(version)
    update_version_info(version)

    try:
        final_exe, exe_name, version_build_dir = build_exe(version)
        cleanup_old_versions(f"{APP_NAME}-v{version}.exe")
        backup_build_script(version, version_build_dir)
    finally:
        restore_version()

    update_version_history(version, exe_name, changes)
    update_version_json(version, exe_name, changes)

    file_size = os.path.getsize(final_exe) / (1024 * 1024)
    print(f"\n{'=' * 60}")
    print(f"  ✅ 构建成功!")
    print(f"  📦 EXE: {final_exe}")
    print(f"  📦 运行时: {os.path.join(DEV_DIR, '_internal')}")
    print(f"  📏 EXE大小: {file_size:.1f} MB")
    print(f"  🏷️ 版本: {version}")
    print(f"  🔧 模式: PyInstaller --onefile")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
