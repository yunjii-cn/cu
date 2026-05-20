import sys
import os
import time
import re
import shutil
import subprocess

APP_BASE_NAME = "云集智能文件清理专家"
APP_EXE_NAME = "云集智能文件清理专家.exe"
LOCK_FILE = ".yunji.lock"


def _create_hardlink(src, dst):
    try:
        if os.path.exists(dst):
            os.remove(dst)
        os.link(src, dst)
        return True
    except Exception:
        pass
    try:
        if os.path.exists(dst):
            os.remove(dst)
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False


def _find_dev_dir_by_lock(exe_path):
    exe_dir = os.path.dirname(exe_path)
    search_dir = exe_dir
    for _ in range(5):
        if os.path.exists(os.path.join(search_dir, LOCK_FILE)):
            return search_dir
        if os.path.exists(os.path.join(search_dir, "app")):
            return search_dir
        parent = os.path.dirname(search_dir)
        if parent == search_dir:
            break
        search_dir = parent
    return None


def _find_dev_dir(exe_path):
    result = _find_dev_dir_by_lock(exe_path)
    if result is not None:
        return result
    exe_dir = os.path.dirname(exe_path)
    if os.path.basename(exe_dir) == "ver":
        return os.path.dirname(exe_dir)
    if os.path.exists(os.path.join(exe_dir, "ver")):
        return exe_dir
    return None


def _cleanup_root_versioned_exes(dev_dir, current_exe_path):
    ver_dir = os.path.join(dev_dir, "ver")
    if not os.path.isdir(ver_dir):
        return
    for f in os.listdir(dev_dir):
        if not re.search(r'-v\d{4}\.\d{2}\.\d{2}\.\d{4}', f):
            continue
        if not f.lower().endswith('.exe'):
            continue
        root_exe = os.path.join(dev_dir, f)
        if os.path.abspath(root_exe) == current_exe_path:
            continue
        ver_exe = os.path.join(ver_dir, f)
        if os.path.exists(ver_exe):
            try:
                os.remove(root_exe)
            except Exception:
                pass


def _self_deploy(exe_path):
    exe_dir = os.path.dirname(exe_path)
    exe_name = os.path.basename(exe_path)

    deploy_dir = os.path.join(exe_dir, APP_BASE_NAME)
    os.makedirs(deploy_dir, exist_ok=True)

    ver_dir = os.path.join(deploy_dir, "ver")
    os.makedirs(ver_dir, exist_ok=True)

    app_dir = os.path.join(deploy_dir, "app")
    os.makedirs(app_dir, exist_ok=True)

    lock_path = os.path.join(deploy_dir, LOCK_FILE)
    if not os.path.exists(lock_path):
        with open(lock_path, "w", encoding="utf-8") as f:
            f.write(APP_BASE_NAME)

    m = re.search(r'-v\d{4}\.\d{2}\.\d{2}\.\d{4}', exe_name)
    if m:
        ver_exe = os.path.join(ver_dir, exe_name)
        if not os.path.exists(ver_exe):
            try:
                shutil.copy2(exe_path, ver_exe)
            except Exception:
                ver_exe = exe_path

        dev_exe = os.path.join(deploy_dir, APP_EXE_NAME)
        try:
            if os.path.exists(dev_exe) and os.path.samefile(dev_exe, ver_exe):
                return deploy_dir
        except Exception:
            pass
        _create_hardlink(ver_exe, dev_exe)
    else:
        dev_exe = os.path.join(deploy_dir, APP_EXE_NAME)
        if not os.path.exists(dev_exe):
            try:
                shutil.copy2(exe_path, dev_exe)
            except Exception:
                pass

    return deploy_dir


def _relocate_if_needed():
    if not getattr(sys, 'frozen', False):
        return

    exe_path = os.path.abspath(sys.executable)
    exe_dir = os.path.dirname(exe_path)
    exe_name = os.path.basename(exe_path)

    dev_dir = _find_dev_dir(exe_path)
    if dev_dir is not None:
        _cleanup_root_versioned_exes(dev_dir, exe_path)
        lock_path = os.path.join(dev_dir, LOCK_FILE)
        if not os.path.exists(lock_path):
            with open(lock_path, "w", encoding="utf-8") as f:
                f.write(APP_BASE_NAME)
        return

    m = re.search(r'-v\d{4}\.\d{2}\.\d{2}\.\d{4}', exe_name)
    if m:
        deploy_dir = _self_deploy(exe_path)
        return

    if os.path.basename(exe_dir) == "ver":
        return

    dev_dir = exe_dir
    ver_dir = os.path.join(dev_dir, "ver")
    os.makedirs(ver_dir, exist_ok=True)

    lock_path = os.path.join(dev_dir, LOCK_FILE)
    if not os.path.exists(lock_path):
        with open(lock_path, "w", encoding="utf-8") as f:
            f.write(APP_BASE_NAME)

    if m:
        ver_exe = os.path.join(ver_dir, exe_name)
        if not os.path.exists(ver_exe):
            _create_hardlink(exe_path, ver_exe)

        dev_exe = os.path.join(dev_dir, APP_EXE_NAME)
        try:
            if os.path.exists(dev_exe) and os.path.samefile(dev_exe, ver_exe):
                return
        except Exception:
            pass
        _create_hardlink(ver_exe, dev_exe)


_relocate_if_needed()

if sys.platform == 'win32':
    try:
        import psutil
        current_pid = os.getpid()
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pname = proc.info['name']
                if pname and pname.lower().startswith(APP_BASE_NAME) and pname.lower().endswith('.exe'):
                    if proc.info['pid'] != current_pid:
                        proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        time.sleep(0.3)
    except Exception:
        pass

    try:
        ctypes = __import__('ctypes')
        EVENT_MODIFY_STATE = 0x0002
        WAIT_OBJECT_0 = 0x00000000
        INFINITE = 0xFFFFFFFF
        INSTANCE_EVENT = "YunJiCleanup_SingleInstance_Event"

        handle = ctypes.windll.kernel32.CreateEventW(None, True, False, INSTANCE_EVENT)
        if handle == 0:
            pass
        elif ctypes.windll.kernel32.GetLastError() == 183:
            ctypes.windll.kernel32.CloseHandle(handle)
            old = ctypes.windll.kernel32.OpenEventW(EVENT_MODIFY_STATE, False, INSTANCE_EVENT)
            if old:
                ctypes.windll.kernel32.SetEvent(old)
                ctypes.windll.kernel32.CloseHandle(old)
            time.sleep(0.3)
            handle = ctypes.windll.kernel32.CreateEventW(None, True, False, INSTANCE_EVENT)
        if handle:
            def _wait_for_signal():
                ctypes.windll.kernel32.WaitForSingleObject(handle, INFINITE)
                ctypes.windll.kernel32.CloseHandle(handle)
                os._exit(0)
            t = __import__('threading').Thread(target=_wait_for_signal, daemon=True)
            t.start()

        ctypes.windll.kernel32.FreeConsole()
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import main
main.main()
