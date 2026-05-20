import os
import sys
import json
import re
import shutil
import subprocess
import urllib.request
import concurrent.futures
import threading
import tkinter as tk


APP_NAME = "云集智能文件清理专家"
APP_EXE_NAME = f"{APP_NAME}.exe"
GITHUB_REPO = "yunjii-cn/cu"
GITEE_REPO = "yunjii/cu"
VERSION_JSON_PATH = "dev/ver/version.json"

COLOR_BG = "#1e1e2e"
COLOR_CARD = "#2a2a3a"
COLOR_ACCENT = "#4a9eff"
COLOR_TEXT = "#e0e0e0"
COLOR_DIM = "#888888"
COLOR_SUCCESS = "#4caf50"
COLOR_ERROR = "#ef5350"


def _fetch_json(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_latest_version():
    urls = [
        (f"https://gitee.com/{GITEE_REPO}/raw/main/{VERSION_JSON_PATH}", "Gitee"),
        (f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{VERSION_JSON_PATH}", "GitHub"),
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(_fetch_json, url): src for url, src in urls}
        for future in concurrent.futures.as_completed(futures):
            try:
                return future.result()
            except Exception:
                continue
    return None


def _find_existing_latest(ver_dir):
    if not os.path.isdir(ver_dir):
        return None, None
    best = None
    best_ver = ""
    for f in os.listdir(ver_dir):
        if not f.endswith(".exe") or APP_NAME not in f:
            continue
        m = re.search(r'v(\d+\.\d+\.\d+\.\d+)', f)
        if m:
            ver = m.group(1)
            if ver > best_ver:
                best_ver = ver
                best = f
    return best, best_ver


class DownloaderApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} - 安装")
        self.root.configure(bg=COLOR_BG)
        self.root.resizable(False, False)
        self.root.overruled = False

        w, h = 460, 280
        sx = (self.root.winfo_screenwidth() - w) // 2
        sy = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{sx}+{sy}")

        self._build_ui()

        self.root.after(100, self._start)

    def _build_ui(self):
        main = tk.Frame(self.root, bg=COLOR_BG)
        main.pack(fill="both", expand=True, padx=30, pady=20)

        self.title_label = tk.Label(
            main, text=APP_NAME, font=("Microsoft YaHei UI", 16, "bold"),
            fg=COLOR_TEXT, bg=COLOR_BG)
        self.title_label.pack(pady=(0, 5))

        self.subtitle_label = tk.Label(
            main, text="正在初始化...", font=("Microsoft YaHei UI", 10),
            fg=COLOR_DIM, bg=COLOR_BG)
        self.subtitle_label.pack(pady=(0, 15))

        self.progress = tk.Canvas(main, width=400, height=8, bg="#333345",
                                  highlightthickness=0)
        self.progress.pack(pady=(0, 10))

        self.detail_label = tk.Label(
            main, text="", font=("Microsoft YaHei UI", 9),
            fg=COLOR_DIM, bg=COLOR_BG, wraplength=400, justify="left")
        self.detail_label.pack(pady=(0, 10))

        self.status_label = tk.Label(
            main, text="", font=("Microsoft YaHei UI", 9),
            fg=COLOR_ACCENT, bg=COLOR_BG)
        self.status_label.pack()

    def _set_progress(self, pct):
        self.progress.delete("bar")
        w = 400
        fill_w = int(w * pct / 100)
        if fill_w > 0:
            self.progress.create_rectangle(0, 0, fill_w, 8, fill=COLOR_ACCENT,
                                           outline="", tags="bar")

    def _set_subtitle(self, text):
        self.subtitle_label.config(text=text)

    def _set_detail(self, text):
        self.detail_label.config(text=text)

    def _set_status(self, text, color=COLOR_ACCENT):
        self.status_label.config(text=text, fg=color)

    def _start(self):
        t = threading.Thread(target=self._run, daemon=True)
        t.start()

    def _run(self):
        try:
            self._do_install()
        except Exception as e:
            self.root.after(0, lambda: self._on_error(str(e)))

    def _do_install(self):
        exe_path = os.path.abspath(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
        exe_dir = os.path.dirname(exe_path)
        ver_dir = os.path.join(exe_dir, "ver")
        os.makedirs(ver_dir, exist_ok=True)

        existing_file, existing_ver = _find_existing_latest(ver_dir)

        self.root.after(0, lambda: self._set_subtitle("正在获取版本信息..."))
        self.root.after(0, lambda: self._set_progress(10))

        data = _get_latest_version()
        if not data:
            if existing_file:
                self.root.after(0, lambda: self._set_subtitle("网络不可用，使用已安装版本"))
                self.root.after(0, lambda: self._set_detail(f"已安装: {existing_ver}"))
                self.root.after(0, lambda: self._set_progress(100))
                self._launch_and_exit(os.path.join(ver_dir, existing_file), exe_path, exe_dir)
                return
            self.root.after(0, lambda: self._on_error("无法获取版本信息，请检查网络连接"))
            return

        latest = data.get("latest", "")
        versions = data.get("versions", [])
        entry = next((v for v in versions if v.get("version") == latest), None)
        if not entry:
            self.root.after(0, lambda: self._on_error("版本信息格式错误"))
            return

        filename = entry.get("filename") or entry.get("exe") or ""
        version = entry.get("version", "")
        changes = entry.get("changes", [])

        if not filename:
            self.root.after(0, lambda: self._on_error("版本文件信息缺失"))
            return

        local_name = entry.get("exe") or filename
        if not local_name.startswith(APP_NAME):
            local_name = f"{APP_NAME}-v{version}.exe"

        self.root.after(0, lambda: self._set_subtitle(f"最新版本: {version}"))
        if changes:
            self.root.after(0, lambda: self._set_detail(changes[0]))
        self.root.after(0, lambda: self._set_progress(20))

        ver_exe = os.path.join(ver_dir, local_name)

        if os.path.exists(ver_exe):
            self.root.after(0, lambda: self._set_subtitle(f"版本 {version} 已安装"))
            self.root.after(0, lambda: self._set_progress(90))
        else:
            size_mb = entry.get("size_mb", "?")
            self.root.after(0, lambda: self._set_subtitle(f"正在下载 {version} ({size_mb} MB)"))
            self.root.after(0, lambda: self._set_progress(25))

            urls = [
                f"https://gitee.com/{GITEE_REPO}/releases/download/v{version}/{filename}",
                f"https://github.com/{GITHUB_REPO}/releases/download/v{version}/{filename}",
            ]
            ok = False
            for url in urls:
                src = "Gitee" if "gitee.com" in url else "GitHub"
                self.root.after(0, lambda s=src: self._set_status(f"下载源: {s}"))
                try:
                    tmp_path = os.path.join(ver_dir, filename)
                    self._download_with_progress(url, tmp_path)
                    if tmp_path != ver_exe:
                        shutil.move(tmp_path, ver_exe)
                    ok = True
                    break
                except Exception as e:
                    for p in [tmp_path, ver_exe]:
                        if os.path.exists(p):
                            try:
                                os.remove(p)
                            except Exception:
                                pass
                    continue
            if not ok:
                self.root.after(0, lambda: self._on_error("所有下载源均失败，请检查网络"))
                return

        self.root.after(0, lambda: self._set_subtitle("正在启动..."))
        self.root.after(0, lambda: self._set_progress(100))
        self.root.after(0, lambda: self._set_status("完成！", COLOR_SUCCESS))

        self._launch_and_exit(ver_exe, exe_path, exe_dir)

    def _download_with_progress(self, url, dest, timeout=300):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            with open(dest, "wb") as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = 25 + int(downloaded * 65 / total)
                        mb = downloaded / (1024 * 1024)
                        total_mb = total / (1024 * 1024)
                        self.root.after(0, lambda p=pct, m=mb, t=total_mb: (
                            self._set_progress(p),
                            self._set_detail(f"{m:.1f} / {t:.1f} MB")
                        ))

    def _launch_and_exit(self, ver_exe, current_exe_path, exe_dir):
        dev_exe = os.path.join(exe_dir, APP_EXE_NAME)

        subprocess.Popen(f'start "" "{ver_exe}"', shell=True,
                         creationflags=subprocess.CREATE_NO_WINDOW)

        if os.path.abspath(current_exe_path) == os.path.abspath(dev_exe):
            replace_cmd = (f'ping -n 3 127.0.0.1 >nul & '
                           f'del /f "{dev_exe}" & '
                           f'mklink /h "{dev_exe}" "{ver_exe}"')
            subprocess.Popen(replace_cmd, shell=True,
                             creationflags=subprocess.CREATE_NO_WINDOW)

        self.root.after(800, self.root.destroy)

    def _on_error(self, msg):
        self._set_subtitle("安装失败")
        self._set_detail(msg)
        self._set_status("点击关闭", COLOR_ERROR)
        self._set_progress(0)
        self.root.after(5000, self.root.destroy)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = DownloaderApp()
    app.run()
