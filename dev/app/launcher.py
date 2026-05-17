import sys
import os
import time

APP_BASE_NAME = "云集智能文件清理专家"

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
