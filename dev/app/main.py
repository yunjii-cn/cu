#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
from PIL import Image, ImageTk
import os
import sys
import json
import hashlib
import threading
from datetime import datetime, timedelta
import time
import re
import psutil
import shutil
import zipfile

VERSION = "DEV"
VERSION_CHECK_URL = "https://gitee.com/yunjii/cleanup/raw/master/ver/version.json"
APP_NAME = f"云集智能文件清理专家 v{VERSION}"

COLOR_RED = "#CC0000"
COLOR_RED_LIGHT = "#FF0000"
COLOR_BG = "#1a1a1a"
COLOR_BORDER = "#333333"
COLOR_TEXT = "#ffffff"
COLOR_DIM = "#888888"

CATEGORY_COLORS_DEFAULT = {
    "temp": "#4a2020",
    "sys_tmp": "#4a2520",
    "backup": "#4a3020",
    "log_file": "#304a20",
    "editor_tmp": "#204a25",
    "ghost_img": "#204a30",
    "download_group": "#20204a",
    "thunder": "#25204a",
    "browser_dl": "#30204a",
    "dl_links": "#20304a",
    "emule_tmp": "#20354a",
    "cache": "#4a4a20",
    "sys_cache": "#4a3520",
    "db_cache": "#354a20",
    "data_file": "#2a4a20",
    "crash_dump": "#4a2a20",
    "ads": "#4a2035",
    "ad_file": "#4a2030",
    "track_data": "#35204a",
    "ad_image": "#4a2535",
    "ad_link": "#30204a",
    "empty_folders": "#282828",
    "duplicates": "#2a2a3a",
    "custom": "#20204a",
}

CATEGORY_TEXT_COLORS = {
    "temp": "#ff6666",
    "sys_tmp": "#ff7766",
    "backup": "#ff9966",
    "log_file": "#88cc44",
    "editor_tmp": "#44cc88",
    "ghost_img": "#44ccaa",
    "download_group": "#6666ff",
    "thunder": "#7766ff",
    "browser_dl": "#9966ff",
    "dl_links": "#6699ff",
    "emule_tmp": "#66aaff",
    "cache": "#cccc44",
    "sys_cache": "#cc9944",
    "db_cache": "#88cc44",
    "data_file": "#55cc44",
    "crash_dump": "#cc6644",
    "ads": "#cc44aa",
    "ad_file": "#cc4488",
    "track_data": "#8844cc",
    "ad_image": "#cc5588",
    "ad_link": "#9944cc",
    "empty_folders": "#888888",
    "duplicates": "#8888cc",
    "custom": "#6666ff",
}

CATEGORY_TREE = {
    "temp": {
        "name": "临时文件",
        "color": "temp",
        "tooltip": "系统临时文件、备份、日志、编辑器临时文件等",
        "children": ["sys_tmp", "backup", "log_file", "editor_tmp", "ghost_img"],
    },
    "sys_tmp": {
        "name": "系统临时",
        "parent": "temp",
        "color": "sys_tmp",
        "tooltip": ".tmp .temp - 系统和应用程序生成的临时文件",
        "extensions": {'.tmp': '系统临时文件', '.temp': '临时文件'},
    },
    "backup": {
        "name": "备份文件",
        "parent": "temp",
        "color": "backup",
        "tooltip": ".bak .old - 程序自动生成的备份和旧版本文件",
        "extensions": {'.bak': '备份文件', '.old': '旧文件'},
    },
    "log_file": {
        "name": "日志文件",
        "parent": "temp",
        "color": "log_file",
        "tooltip": ".log - 应用程序运行日志文件",
        "extensions": {'.log': '日志文件'},
    },
    "editor_tmp": {
        "name": "编辑器临时",
        "parent": "temp",
        "color": "editor_tmp",
        "tooltip": ".swp .swo .swn .~$ - Vim/Office等编辑器临时文件",
        "extensions": {'.swp': 'Vim临时', '.swo': 'Vim临时', '.swn': 'Vim临时', '.~$': 'Office临时'},
    },
    "ghost_img": {
        "name": "镜像备份",
        "parent": "temp",
        "color": "ghost_img",
        "tooltip": ".gho .ghs - Ghost备份镜像文件",
        "extensions": {'.gho': 'Ghost备份', '.ghs': 'Ghost镜像'},
    },
    "download_group": {
        "name": "下载相关",
        "color": "download_group",
        "tooltip": "迅雷/浏览器/电驴等下载工具产生的临时文件和链接",
        "children": ["thunder", "browser_dl", "dl_links", "emule_tmp"],
    },
    "thunder": {
        "name": "迅雷临时",
        "parent": "download_group",
        "color": "thunder",
        "tooltip": ".td .ttd .xltd .bt.td等 - 迅雷下载器未完成的临时文件",
        "extensions": {
            '.td': '迅雷未完成下载', '.ttd': '迅雷临时数据', '.tdcfg': '迅雷下载配置',
            '.xltd': '迅雷极速版临时', '.xltdcfg': '迅雷极速版配置',
            '.xltd.td': '迅雷复合临时', '.xltd.ltd': '迅雷复合数据', '.bt.td': '迅雷BT临时',
        },
        "name_patterns": [(r'.*\.td_\d+$', '迅雷分片'), (r'.*xltd_\d+$', '迅雷极速版分片')],
    },
    "browser_dl": {
        "name": "浏览器下载",
        "parent": "download_group",
        "color": "browser_dl",
        "tooltip": ".download .crdownload .part .incomplete - 浏览器未完成的下载文件",
        "extensions": {
            '.download': '浏览器下载', '.incomplete': '未完成下载',
            '.part': '部分下载', '.crdownload': 'Chrome下载',
        },
    },
    "dl_links": {
        "name": "下载链接",
        "parent": "download_group",
        "color": "dl_links",
        "tooltip": ".torrent .magnet .thunder .ed2k - 种子和下载协议链接文件",
        "extensions": {
            '.torrent': '种子文件', '.magnet': '磁链文件',
            '.ed2k': '电驴链接', '.thunder': '迅雷链接', '.flashget': '快车链接',
        },
    },
    "emule_tmp": {
        "name": "电驴临时",
        "parent": "download_group",
        "color": "emule_tmp",
        "tooltip": ".part.met .corrupt .met - 电驴下载器临时和损坏文件",
        "extensions": {'.part.met': '电驴元数据', '.corrupt': '电驴损坏文件', '.met': '电驴元数据'},
    },
    "cache": {
        "name": "缓存文件",
        "color": "cache",
        "tooltip": "系统缓存、数据库缓存、崩溃转储等",
        "children": ["sys_cache", "db_cache", "data_file", "crash_dump"],
    },
    "sys_cache": {
        "name": "系统缓存",
        "parent": "cache",
        "color": "sys_cache",
        "tooltip": ".cache .thumb .db Thumbs.db等 - 系统和应用缓存文件",
        "extensions": {
            '.cache': '缓存文件', '.thumb': '缩略图缓存', '.thumbnail': '缩略图',
        },
        "system_files": {
            'Thumbs.db': '系统缩略图缓存', 'ehthumbs.db': '视频缩略图缓存',
            'Desktop.ini': '桌面配置文件', 'iconcache.db': '图标缓存',
        },
    },
    "db_cache": {
        "name": "数据库缓存",
        "parent": "cache",
        "color": "db_cache",
        "tooltip": ".db .sqlite .sqlite3 .ndb - 数据库缓存文件",
        "extensions": {'.db': '数据库缓存', '.sqlite': 'SQLite缓存', '.sqlite3': 'SQLite缓存', '.ndb': '网络数据库'},
    },
    "data_file": {
        "name": "数据文件",
        "parent": "cache",
        "color": "data_file",
        "tooltip": ".dat .idx - 索引和数据文件",
        "extensions": {'.dat': '数据文件', '.idx': '索引文件'},
    },
    "crash_dump": {
        "name": "崩溃转储",
        "parent": "cache",
        "color": "crash_dump",
        "tooltip": ".crash .dmp .dump .core - 崩溃报告和内存转储文件",
        "extensions": {'.crash': '崩溃报告', '.dmp': '内存转储', '.dump': '转储文件', '.core': '核心转储'},
    },
    "ads": {
        "name": "广告追踪",
        "color": "ads",
        "tooltip": "广告脚本、追踪数据、广告图片和链接",
        "children": ["ad_file", "track_data", "ad_image", "ad_link"],
    },
    "ad_file": {
        "name": "广告文件",
        "parent": "ads",
        "color": "ad_file",
        "tooltip": ".ad .ads - 广告脚本和广告文件",
        "extensions": {'.ad': '广告文件', '.ads': '广告脚本'},
    },
    "track_data": {
        "name": "追踪数据",
        "parent": "ads",
        "color": "track_data",
        "tooltip": ".tracking .analytics .metrics - 用户行为追踪和分析数据",
        "extensions": {'.tracking': '追踪文件', '.analytics': '分析数据', '.metrics': '度量数据'},
    },
    "ad_image": {
        "name": "广告图片",
        "parent": "ads",
        "color": "ad_image",
        "tooltip": "文件名含banner/ad/adv/promo/sponsor/popup的图片文件",
        "extensions": {},
        "image_patterns": [
            r'.*banner.*\.(jpg|jpeg|png|gif|webp|bmp|svg)$',
            r'.*ad[_\-].*\.(jpg|jpeg|png|gif|webp|bmp|svg)$',
            r'.*adv[_\-].*\.(jpg|jpeg|png|gif|webp|bmp|svg)$',
            r'.*promo.*\.(jpg|jpeg|png|gif|webp|bmp|svg)$',
            r'.*sponsor.*\.(jpg|jpeg|png|gif|webp|bmp|svg)$',
            r'.*popup.*\.(jpg|jpeg|png|gif|webp|bmp|svg)$',
        ],
    },
    "ad_link": {
        "name": "广告链接",
        "parent": "ads",
        "color": "ad_link",
        "tooltip": "文件名含ad_track/click_track/pixel_track/analytics_log的文件",
        "extensions": {},
        "link_patterns": [
            r'.*ad[_\-]?track.*',
            r'.*click[_\-]?track.*',
            r'.*pixel[_\-]?track.*',
            r'.*analytics[_\-]?log.*',
            r'.*redirect[_\-]?link.*',
        ],
    },
    "empty_folders": {
        "name": "空文件夹",
        "color": "empty_folders",
        "tooltip": "不包含任何文件或子文件夹的空目录",
        "extensions": {},
    },
}

CATEGORY_TO_CHECKBOX = {}
for _cid, _cinfo in CATEGORY_TREE.items():
    _cname = _cinfo["name"]
    CATEGORY_TO_CHECKBOX[_cname] = _cid
    if "extensions" in _cinfo:
        for _ext, _desc in _cinfo["extensions"].items():
            CATEGORY_TO_CHECKBOX[_desc] = _cid
    if "system_files" in _cinfo:
        for _fn, _desc in _cinfo["system_files"].items():
            CATEGORY_TO_CHECKBOX[_desc] = _cid
    if "name_patterns" in _cinfo:
        for _pat, _desc in _cinfo["name_patterns"]:
            CATEGORY_TO_CHECKBOX[_desc] = _cid
CATEGORY_TO_CHECKBOX["广告图片"] = "ad_image"
CATEGORY_TO_CHECKBOX["广告链接"] = "ad_link"
CATEGORY_TO_CHECKBOX["重复文件"] = "duplicates"
CATEGORY_TO_CHECKBOX["自定义规则"] = "custom"

COLUMN_WIDTHS_DEFAULT = {
    "选择": 60, "文件名": 180, "完整路径": 350,
    "大小": 100, "修改时间": 150, "类型": 100, "分类": 100,
}

COLUMN_MIN_WIDTHS = {
    "选择": 55, "文件名": 80, "完整路径": 100,
    "大小": 65, "修改时间": 110, "类型": 55, "分类": 65,
}


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        if self.tip_window:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)
        label = tk.Label(tw, text=self.text, justify="left",
                        background="#333333", foreground="#ffffff",
                        relief="solid", borderwidth=1,
                        font=("Arial", 11), padx=6, pady=4)
        label.pack()

    def hide(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


def get_system_info():
    try:
        mem = psutil.virtual_memory()
        return {
            "total_ram_gb": round(mem.total / (1024**3), 1),
            "cpu_logical": psutil.cpu_count(logical=True),
            "cpu_physical": psutil.cpu_count(logical=False),
        }
    except Exception:
        return {"total_ram_gb": 8, "cpu_logical": 4, "cpu_physical": 2}


def recommend_params(sys_info):
    ram = sys_info["total_ram_gb"]
    if ram >= 64:
        return {"max_display": 50000, "max_depth": 100, "batch_size": 50, "flush_interval": 0.1}
    elif ram >= 32:
        return {"max_display": 30000, "max_depth": 80, "batch_size": 40, "flush_interval": 0.12}
    elif ram >= 16:
        return {"max_display": 15000, "max_depth": 60, "batch_size": 30, "flush_interval": 0.13}
    elif ram >= 8:
        return {"max_display": 8000, "max_depth": 50, "batch_size": 20, "flush_interval": 0.15}
    else:
        return {"max_display": 3000, "max_depth": 30, "batch_size": 15, "flush_interval": 0.2}


def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_app_dir():
    d = os.path.join(get_base_dir(), "app")
    os.makedirs(d, exist_ok=True)
    return d


def load_settings():
    sys_info = get_system_info()
    rec = recommend_params(sys_info)
    path = os.path.join(get_app_dir(), "cleanup_settings.json")
    defaults = {
        "scan_directory": "", "last_scan_time": "",
        "max_display": rec["max_display"], "max_depth": rec["max_depth"],
        "batch_size": rec["batch_size"], "flush_interval": rec["flush_interval"],
        "delete_mode": "permanent", "delete_move_dir": "", "delete_zip_name": "cleanup_{date}",
        "category_colors": CATEGORY_COLORS_DEFAULT.copy(),
        "category_enabled": {},
        "custom_rules": [],
        "column_widths": COLUMN_WIDTHS_DEFAULT.copy(),
        "size_enabled": False, "size_operator": ">", "size_value": "", "size_unit": "MB",
        "days_value": "0", "mode_value": "stacked",
        "custom_enabled": False,
    }
    if os.path.isfile(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                defaults.update(saved)
        except Exception:
            pass
    defaults["sys_info"] = sys_info
    defaults["recommended"] = rec
    return defaults


def save_settings(settings):
    path = os.path.join(get_app_dir(), "cleanup_settings.json")
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_scan_results():
    path = os.path.join(get_app_dir(), "scan_results.json")
    if os.path.isfile(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return None


def save_scan_results(data):
    path = os.path.join(get_app_dir(), "scan_results.json")
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


class GarbageCleanupTool:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title(APP_NAME)
        self.root.geometry("1400x800")
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.file_list = []
        self.filtered_files = []
        self.total_size = 0

        self.scanning = False
        self.scan_cancelled = False
        self.processed_items = 0

        self.scan_conditions = {}
        self.custom_rules = []
        self.condition_mode = "stacked"
        self.file_size_condition = None

        self.sort_column = None
        self.sort_reverse = False
        self.selected_files = set()
        self.select_all_var = ctk.BooleanVar(value=True)

        self.settings = load_settings()
        self.delete_mode = self.settings.get("delete_mode", "permanent")
        self.delete_move_dir = self.settings.get("delete_move_dir", "")
        self.delete_zip_name = self.settings.get("delete_zip_name", "cleanup_{date}")
        self.category_colors = {**CATEGORY_COLORS_DEFAULT, **self.settings.get("category_colors", {})}
        self.column_widths = self.settings.get("column_widths", COLUMN_WIDTHS_DEFAULT.copy())
        self.custom_rules = self.settings.get("custom_rules", [])

        self._pending_ui_updates = []
        self._last_ui_flush = 0.0
        self._displayed_count = 0
        self._scan_depth = 0
        self._max_display = self.settings.get("max_display", 5000)
        self._max_depth = self.settings.get("max_depth", 50)
        self._batch_size = self.settings.get("batch_size", 20)
        self._flush_interval = self.settings.get("flush_interval", 0.15)

        self._settings_visible = False
        self._settings_frame = None
        self._delete_settings_visible = False
        self._delete_settings_frame = None
        self._color_settings_visible = False
        self._color_settings_frame = None

        self.preset_vars = {}
        self._prev_column_widths = {}
        self._cat_rows = []
        self._cat_child_rows = {}
        self._cat_color_btns = {}

        self.setup_ui()
        self._set_icon()
        self._try_restore_results()

    def _on_closing(self):
        self._save_all_state()
        self.root.destroy()

    def _save_all_state(self):
        cat_enabled = {}
        for cid, var in self.preset_vars.items():
            cat_enabled[cid] = var.get()
        self.settings["category_enabled"] = cat_enabled
        self.settings["custom_rules"] = self.custom_rules
        self.settings["custom_enabled"] = self.custom_enabled_var.get()
        self._save_column_widths()
        self.settings["size_enabled"] = self.size_enabled_var.get()
        self.settings["size_operator"] = self.size_operator_var.get()
        self.settings["size_value"] = self.size_value_entry.get()
        self.settings["size_unit"] = self.size_unit_var.get()
        self.settings["days_value"] = self.days_var.get()
        self.settings["mode_value"] = self.mode_var.get()
        self.settings["delete_mode"] = self.delete_mode
        self.settings["delete_move_dir"] = self.delete_move_dir
        self.settings["delete_zip_name"] = self.delete_zip_name
        self.settings["category_colors"] = self.category_colors
        self.settings["scan_directory"] = self.dir_entry.get().strip()
        save_settings(self.settings)

    def _set_icon(self):
        base = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base, "icon.ico")
        png_path = os.path.join(base, "icon.png")
        if os.path.isfile(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass
        if os.path.isfile(png_path):
            try:
                pil_img = Image.open(png_path)
                ctk_img = ImageTk.PhotoImage(pil_img)
                self.root.tk.call('wm', 'iconphoto', self.root._w, ctk_img)
                self._icon_img = ctk_img
            except Exception:
                pass

    def setup_ui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Dark.Treeview",
                       background=COLOR_BG, foreground=COLOR_TEXT,
                       fieldbackground=COLOR_BG, borderwidth=0,
                       font=('Arial', 16), rowheight=28, relief="flat")
        style.configure("Dark.Treeview.Heading",
                       background="#252525", foreground=COLOR_TEXT,
                       borderwidth=0,
                       font=('Arial', 16, 'bold'), relief="flat")
        style.map("Dark.Treeview",
                 background=[('selected', COLOR_RED), ('active', '#2a2a2a')],
                 foreground=[('selected', COLOR_TEXT)])
        style.map("Dark.Treeview.Heading", background=[('active', '#333')])

        for cat_id, color in self.category_colors.items():
            tag_name = f"cat_{cat_id}"
            style.configure(tag_name, background=color, foreground=COLOR_TEXT, fieldbackground=color, relief="flat")
            style.map(tag_name,
                     background=[('selected', COLOR_RED), ('active', color)],
                     foreground=[('selected', COLOR_TEXT)])

        style.configure("Dark.Vertical.TScrollbar", background=COLOR_RED, troughcolor=COLOR_BG,
                        bordercolor=COLOR_RED, arrowcolor=COLOR_TEXT, width=12)
        style.map("Dark.Vertical.TScrollbar", background=[('active', COLOR_RED_LIGHT)])
        style.configure("Dark.Horizontal.TScrollbar", background=COLOR_RED, troughcolor=COLOR_BG,
                        bordercolor=COLOR_RED, arrowcolor=COLOR_TEXT, width=12)
        style.map("Dark.Horizontal.TScrollbar", background=[('active', COLOR_RED_LIGHT)])

        self.main_frame = ctk.CTkFrame(self.root, fg_color=COLOR_BG, border_color=COLOR_BORDER, border_width=2)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.setup_control_panel()
        self.setup_scan_conditions()
        self.setup_table_area()
        self.setup_status_bar()

    def _make_color_tag(self, parent, text, cat_id, variable, command, font_size=12):
        color = self.category_colors.get(cat_id, COLOR_BG)
        tag_frame = ctk.CTkFrame(parent, fg_color=color, corner_radius=6)
        tag_frame.pack(side="left", padx=(2, 4), pady=2)

        cb = ctk.CTkCheckBox(tag_frame, text=text, variable=variable, command=command,
                            fg_color=COLOR_RED, hover_color=COLOR_RED_LIGHT,
                            checkmark_color=COLOR_TEXT, text_color=COLOR_TEXT,
                            font=ctk.CTkFont(size=font_size), corner_radius=4,
                            bg_color=color, border_width=0)
        cb.pack(padx=4, pady=2)

        tooltip_text = CATEGORY_TREE.get(cat_id, {}).get("tooltip", "")
        if tooltip_text:
            ToolTip(cb, tooltip_text)
            ToolTip(tag_frame, tooltip_text)

        return tag_frame, cb

    def setup_control_panel(self):
        control_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e1e1e", border_color=COLOR_BORDER, border_width=1)
        control_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(control_frame, text="📁", font=ctk.CTkFont(size=16)).pack(side="left", padx=(10, 3))

        self.dir_entry = ctk.CTkEntry(control_frame, placeholder_text="选择要扫描的目录...",
                                     fg_color="#2a2a2a", border_color="#444",
                                     text_color=COLOR_TEXT, placeholder_text_color=COLOR_DIM, height=34)
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=3, pady=8)
        if self.settings.get("scan_directory"):
            self.dir_entry.insert(0, self.settings["scan_directory"])

        ctk.CTkButton(control_frame, text="浏览", width=60, height=34, command=self.browse_directory,
                     fg_color="#333", hover_color=COLOR_RED, text_color=COLOR_TEXT, font=ctk.CTkFont(size=13)).pack(side="left", padx=3)
        ctk.CTkButton(control_frame, text="🔍 扫描", font=ctk.CTkFont(size=13, weight="bold"), height=34,
                     fg_color=COLOR_RED, hover_color=COLOR_RED_LIGHT, command=self.start_scan).pack(side="left", padx=3)
        self.stop_button = ctk.CTkButton(control_frame, text="⏹ 停止", height=34, command=self.stop_scan,
                                        state="disabled", fg_color="#333", hover_color=COLOR_RED,
                                        text_color=COLOR_TEXT, font=ctk.CTkFont(size=13))
        self.stop_button.pack(side="left", padx=3)
        ctk.CTkButton(control_frame, text="🗑️ 删除选中", font=ctk.CTkFont(size=13, weight="bold"), height=34,
                     fg_color=COLOR_RED, hover_color=COLOR_RED_LIGHT, command=self.delete_selected_files).pack(side="right", padx=(3, 10))

    def setup_scan_conditions(self):
        saved_enabled = self.settings.get("category_enabled", {})

        func_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e1e1e", border_color=COLOR_BORDER, border_width=1)
        func_frame.pack(fill="x", padx=10, pady=(5, 2))

        func_row = ctk.CTkFrame(func_frame, fg_color="#1e1e1e")
        func_row.pack(fill="x", padx=8, pady=6)

        ctk.CTkLabel(func_row, text="快捷功能", font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLOR_DIM).pack(side="left", padx=(0, 8))

        func_buttons = [
            ("🔍 重复检测", self.start_duplicate_scan),
            ("✅ 校验结果", self.verify_results),
            ("⚙ 扫描设置", self.toggle_settings_panel),
            ("🗑 删除设置", self.toggle_delete_settings_panel),
            ("🎨 分类颜色", self.toggle_color_settings_panel),
        ]
        for text, cmd in func_buttons:
            ctk.CTkButton(func_row, text=text, height=26, fg_color="#333", hover_color=COLOR_RED,
                         text_color=COLOR_TEXT, font=ctk.CTkFont(size=12), command=cmd).pack(side="left", padx=3)

        self.cat_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e1e1e", border_color=COLOR_BORDER, border_width=1)
        self.cat_frame.pack(fill="x", padx=10, pady=2)

        cat_grid = ctk.CTkFrame(self.cat_frame, fg_color="#1e1e1e")
        cat_grid.pack(fill="x", padx=8, pady=6)

        ctk.CTkLabel(cat_grid, text="文件类型", font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLOR_DIM).grid(row=0, column=0, padx=(0, 6), sticky="w")

        top_level_cats = [(cid, cinfo) for cid, cinfo in CATEGORY_TREE.items() if cinfo.get("parent") is None]
        COL_WIDTH = 240

        self._cat_rows = []
        self._cat_child_containers = {}
        self._cat_color_btns = {}
        self._cat_tag_frames = {}
        self._child_checkboxes = {}
        self._all_expanded = False

        col_idx = 1
        for cat_id, cat_info in top_level_cats:
            default_val = saved_enabled.get(cat_id, True)
            var = ctk.BooleanVar(value=default_val)
            self.preset_vars[cat_id] = var

            has_children = "children" in cat_info
            cmd = (lambda cid=cat_id: self.on_parent_toggle(cid)) if has_children else self.on_category_toggle

            color = self.category_colors.get(cat_id, COLOR_BG)
            tag_frame = ctk.CTkFrame(cat_grid, fg_color=color, corner_radius=6)
            tag_frame.grid(row=0, column=col_idx, padx=3, pady=2, sticky="ew")
            self._cat_tag_frames[cat_id] = tag_frame

            cb = ctk.CTkCheckBox(tag_frame, text=cat_info["name"], variable=var, command=cmd,
                                fg_color=COLOR_RED, hover_color=COLOR_RED_LIGHT,
                                checkmark_color=COLOR_TEXT, text_color=COLOR_TEXT,
                                font=ctk.CTkFont(size=12), corner_radius=4,
                                bg_color=color, border_width=0)
            cb.pack(side="left", padx=4, pady=2)

            tooltip_text = cat_info.get("tooltip", "")
            if tooltip_text:
                ToolTip(cb, tooltip_text)
                ToolTip(tag_frame, tooltip_text)

            color_btn = ctk.CTkButton(tag_frame, text="🎨", width=24, height=24, fg_color="#444", hover_color=COLOR_RED,
                                     text_color=COLOR_DIM, font=ctk.CTkFont(size=11),
                                     command=lambda cid=cat_id: self._pick_color_inline(cid))
            color_btn.pack(side="left", padx=(0, 4))
            self._cat_color_btns[cat_id] = color_btn

            if has_children:
                child_container = ctk.CTkFrame(cat_grid, fg_color="#1e1e1e", border_width=1, border_color="#333")
                child_container.grid(row=1, column=col_idx, padx=3, pady=(2, 2), sticky="ew")
                child_container.grid_remove()

                for child_id in cat_info.get("children", []):
                    child_info_d = CATEGORY_TREE.get(child_id, {})
                    default_val_c = saved_enabled.get(child_id, True)
                    child_var = ctk.BooleanVar(value=default_val_c)
                    self.preset_vars[child_id] = child_var

                    child_frame = ctk.CTkFrame(child_container, fg_color="#1e1e1e")
                    child_frame.pack(fill="x", pady=1, padx=4)

                    text_color = CATEGORY_TEXT_COLORS.get(child_id, COLOR_TEXT)
                    child_cb = ctk.CTkCheckBox(child_frame, text=child_info_d["name"], variable=child_var,
                                              command=lambda cid=child_id: self.on_child_toggle(cid),
                                              fg_color=COLOR_RED, hover_color=COLOR_RED_LIGHT,
                                              checkmark_color=text_color, text_color=text_color,
                                              font=ctk.CTkFont(size=11), corner_radius=4,
                                              bg_color="#1e1e1e", border_width=0)
                    child_cb.pack(side="left", padx=3, pady=2)

                    self._child_checkboxes[child_id] = child_cb

                    tooltip_text = child_info_d.get("tooltip", "")
                    if tooltip_text:
                        ToolTip(child_cb, tooltip_text)

                    child_color_btn = ctk.CTkButton(child_frame, text="🎨", width=20, height=20, fg_color="#333",
                                                  hover_color=COLOR_RED, text_color=COLOR_DIM, font=ctk.CTkFont(size=9),
                                                  command=lambda cid=child_id: self._pick_color_inline(cid))
                    child_color_btn.pack(side="left", padx=3)
                    self._cat_color_btns[child_id] = child_color_btn

                self._cat_child_containers[cat_id] = child_container

            cat_grid.grid_columnconfigure(col_idx, minsize=COL_WIDTH)
            col_idx += 1

        expand_btn_frame = ctk.CTkFrame(cat_grid, fg_color="#1e1e1e")
        expand_btn_frame.grid(row=0, column=col_idx, padx=3, pady=2, sticky="w")
        
        self._expand_all_btn = ctk.CTkButton(expand_btn_frame, text="📂 全部展开", width=100, height=28,
                                             fg_color="#333", hover_color=COLOR_RED, text_color=COLOR_TEXT,
                                             font=ctk.CTkFont(size=12), command=self._toggle_all_categories)
        self._expand_all_btn.pack(padx=4, pady=2)

        self.filter_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e1e1e", border_color=COLOR_BORDER, border_width=1)
        self.filter_frame.pack(fill="x", padx=10, pady=2)

        filter_row = ctk.CTkFrame(self.filter_frame, fg_color="#1e1e1e")
        filter_row.pack(fill="x", padx=8, pady=6)

        ctk.CTkLabel(filter_row, text="过滤条件", font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLOR_DIM).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(filter_row, text="时间 ≥", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT).pack(side="left", padx=(0, 2))

        self.days_var = ctk.CTkComboBox(filter_row, values=["0", "7", "30", "90", "180", "365"],
                                       width=65, height=26, fg_color="#2a2a2a", border_color="#444",
                                       text_color=COLOR_TEXT, dropdown_fg_color="#2a2a2a",
                                       dropdown_hover_color=COLOR_RED_LIGHT, dropdown_text_color=COLOR_TEXT,
                                       button_color=COLOR_RED, button_hover_color=COLOR_RED_LIGHT,
                                       font=ctk.CTkFont(size=12), command=lambda v: self._auto_save())
        self.days_var.set(self.settings.get("days_value", "0"))
        self.days_var.pack(side="left", padx=(0, 2))

        ctk.CTkLabel(filter_row, text="天前", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT).pack(side="left", padx=(0, 12))

        self.size_enabled_var = ctk.BooleanVar(value=self.settings.get("size_enabled", False))
        ctk.CTkCheckBox(filter_row, text="大小", variable=self.size_enabled_var,
                       command=self.toggle_file_size_condition, fg_color=COLOR_RED, hover_color=COLOR_RED_LIGHT,
                       checkmark_color=COLOR_TEXT, text_color=COLOR_TEXT, font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 2))

        self.size_operator_var = ctk.StringVar(value=self.settings.get("size_operator", ">"))
        ctk.CTkOptionMenu(filter_row, variable=self.size_operator_var, values=[">", "<"],
                        command=lambda v: self.update_file_size_condition(), width=45, height=26,
                        fg_color="#2a2a2a", button_color=COLOR_RED, button_hover_color=COLOR_RED_LIGHT,
                        text_color=COLOR_TEXT, dropdown_fg_color="#2a2a2a",
                        dropdown_hover_color=COLOR_RED_LIGHT, dropdown_text_color=COLOR_TEXT,
                        font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 2))

        self.size_value_entry = ctk.CTkEntry(filter_row, placeholder_text="值", width=55, height=26,
                                           fg_color="#2a2a2a", border_color="#444", text_color=COLOR_TEXT,
                                           placeholder_text_color=COLOR_DIM, font=ctk.CTkFont(size=12))
        sv = self.settings.get("size_value", "")
        if sv:
            self.size_value_entry.insert(0, sv)
        self.size_value_entry.pack(side="left", padx=(0, 2))

        self.size_unit_var = ctk.StringVar(value=self.settings.get("size_unit", "MB"))
        ctk.CTkOptionMenu(filter_row, variable=self.size_unit_var, values=["KB", "MB", "GB"],
                        command=lambda v: self.update_file_size_condition(), width=50, height=26,
                        fg_color="#2a2a2a", button_color=COLOR_RED, button_hover_color=COLOR_RED_LIGHT,
                        text_color=COLOR_TEXT, dropdown_fg_color="#2a2a2a",
                        dropdown_hover_color=COLOR_RED_LIGHT, dropdown_text_color=COLOR_TEXT,
                        font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 12))

        self.mode_var = ctk.StringVar(value=self.settings.get("mode_value", "stacked"))
        ctk.CTkOptionMenu(filter_row, variable=self.mode_var, values=["stacked", "filtered"],
                        command=lambda v: self._auto_save(), width=70, height=26,
                        fg_color="#2a2a2a", button_color=COLOR_RED, button_hover_color=COLOR_RED_LIGHT,
                        text_color=COLOR_TEXT, dropdown_fg_color="#2a2a2a",
                        dropdown_hover_color=COLOR_RED_LIGHT, dropdown_text_color=COLOR_TEXT,
                        font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 2))
        ctk.CTkLabel(filter_row, text="叠加|筛选", font=ctk.CTkFont(size=10), text_color=COLOR_DIM).pack(side="left")

        self.custom_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e1e1e", border_color=COLOR_BORDER, border_width=1)
        self.custom_frame.pack(fill="x", padx=10, pady=2)

        custom_row = ctk.CTkFrame(self.custom_frame, fg_color="#1e1e1e")
        custom_row.pack(fill="x", padx=8, pady=6)

        self.custom_enabled_var = ctk.BooleanVar(value=self.settings.get("custom_enabled", False))
        self._make_color_tag(custom_row, "自定义规则", "custom", self.custom_enabled_var,
                            self.on_category_toggle, font_size=12)

        self.custom_rule_type_var = ctk.StringVar(value="suffix")
        ctk.CTkOptionMenu(custom_row, variable=self.custom_rule_type_var,
                        values=["suffix", "regex", "name_fuzzy", "name_exact"],
                        width=90, height=26, fg_color="#2a2a2a", button_color=COLOR_RED,
                        button_hover_color=COLOR_RED_LIGHT, text_color=COLOR_TEXT,
                        dropdown_fg_color="#2a2a2a", dropdown_hover_color=COLOR_RED_LIGHT,
                        dropdown_text_color=COLOR_TEXT, font=ctk.CTkFont(size=11)).pack(side="left", padx=(4, 4))

        self.custom_rule_entry = ctk.CTkEntry(custom_row, placeholder_text="后缀/正则/文件名...",
                                             fg_color="#2a2a2a", border_color="#444", text_color=COLOR_TEXT,
                                             placeholder_text_color=COLOR_DIM, height=26, font=ctk.CTkFont(size=12))
        self.custom_rule_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))

        ctk.CTkButton(custom_row, text="+", width=26, height=26, command=self.add_custom_rule,
                     fg_color=COLOR_RED, hover_color=COLOR_RED_LIGHT, text_color=COLOR_TEXT,
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0, 2))
        ctk.CTkButton(custom_row, text="✕", width=26, height=26, command=self.clear_custom_rules,
                     fg_color="#333", hover_color=COLOR_RED, text_color=COLOR_TEXT,
                     font=ctk.CTkFont(size=11)).pack(side="left")

        self.rules_list_frame = ctk.CTkFrame(self.custom_frame, height=36,
                                                      fg_color="#1e1e1e", border_color="#333",
                                                      border_width=1)
        self.rules_list_frame.pack(fill="x", padx=8, pady=(0, 6))
        self.rules_list_frame.pack_propagate(False)

        self._rebuild_rules_display()
        self.update_scan_conditions()

    def on_parent_toggle(self, parent_id):
        parent_var = self.preset_vars.get(parent_id)
        if not parent_var:
            return
        checked = parent_var.get()
        cat_info = CATEGORY_TREE.get(parent_id, {})
        for child_id in cat_info.get("children", []):
            child_var = self.preset_vars.get(child_id)
            if child_var:
                child_var.set(checked)
        self.on_category_toggle()

    def _toggle_all_categories(self):
        self._all_expanded = not self._all_expanded
        for cat_id, child_container in self._cat_child_containers.items():
            if self._all_expanded:
                child_container.grid()
            else:
                child_container.grid_remove()
        self._expand_all_btn.configure(text="📂 全部折叠" if self._all_expanded else "📂 全部展开")

    def _pick_color_inline(self, cat_id):
        current = self.category_colors.get(cat_id, COLOR_BG)
        result = colorchooser.askcolor(color=current, title="选择颜色")
        if result and result[1]:
            self.category_colors[cat_id] = result[1]
            self._update_tag_styles()
            self._auto_save()

    def _update_tag_styles(self):
        for cat_id, color in self.category_colors.items():
            tag_name = f"cat_{cat_id}"
            text_color = CATEGORY_TEXT_COLORS.get(cat_id, COLOR_TEXT)
            self.tree.tag_configure(tag_name, background=color, foreground=text_color)
            tag_frame = self._cat_tag_frames.get(cat_id)
            if tag_frame:
                tag_frame.configure(fg_color=color)
                for child in tag_frame.winfo_children():
                    if isinstance(child, ctk.CTkCheckBox):
                        child.configure(bg_color=color)
        for child_id, child_cb in self._child_checkboxes.items():
            text_color = CATEGORY_TEXT_COLORS.get(child_id, COLOR_TEXT)
            child_cb.configure(text_color=text_color, checkmark_color=text_color)
        self._auto_save()

    def on_child_toggle(self, child_id):
        cat_info = CATEGORY_TREE.get(child_id, {})
        parent_id = cat_info.get("parent")
        if parent_id:
            parent_info = CATEGORY_TREE.get(parent_id, {})
            any_checked = False
            for sibling_id in parent_info.get("children", []):
                sv = self.preset_vars.get(sibling_id)
                if sv and sv.get():
                    any_checked = True
                    break
            parent_var = self.preset_vars.get(parent_id)
            if parent_var:
                parent_var.set(any_checked)
        self.on_category_toggle()

    def on_category_toggle(self):
        self.update_scan_conditions()
        self.sync_selection_with_categories()
        self._auto_save()

    def sync_selection_with_categories(self):
        active = set()
        for cid, var in self.preset_vars.items():
            if var.get():
                active.add(cid)
        if self.custom_enabled_var.get():
            active.add("custom")

        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            tags = self.tree.item(item, "tags")
            file_path = tags[0] if tags else ""
            category = values[6] if len(values) > 6 else ""
            cat_key = CATEGORY_TO_CHECKBOX.get(category, "")
            if cat_key and cat_key in active:
                self.selected_files.add(file_path)
                self.tree.item(item, values=("☑", *values[1:]))
            else:
                self.selected_files.discard(file_path)
                self.tree.item(item, values=("☐", *values[1:]))
        self._update_selected_size_display()

    def toggle_settings_panel(self):
        self._close_other_panels("settings")
        if self._settings_visible:
            if self._settings_frame:
                self._settings_frame.destroy()
                self._settings_frame = None
            self._settings_visible = False
            return
        self._settings_visible = True
        sys_info = self.settings.get("sys_info", get_system_info())
        rec = self.settings.get("recommended", recommend_params(sys_info))
        self._settings_frame = ctk.CTkFrame(self.cat_frame, fg_color="#252525", border_color="#444", border_width=1)
        self._settings_frame.pack(fill="x", padx=10, pady=(0, 8))
        hw_row = ctk.CTkFrame(self._settings_frame, fg_color="#252525")
        hw_row.pack(fill="x", padx=10, pady=(8, 4))
        ctk.CTkLabel(hw_row, text=f"💻 {sys_info['total_ram_gb']}GB | {sys_info['cpu_physical']}核{sys_info['cpu_logical']}线程",
                    font=ctk.CTkFont(size=12), text_color=COLOR_DIM).pack(side="left")
        params_row = ctk.CTkFrame(self._settings_frame, fg_color="#252525")
        params_row.pack(fill="x", padx=10, pady=4)
        self._settings_entries = {}
        items = [
            ("max_display", "显示上限", str(self._max_display), str(rec["max_display"])),
            ("max_depth", "递归深度", str(self._max_depth), str(rec["max_depth"])),
            ("batch_size", "批量大小", str(self._batch_size), str(rec["batch_size"])),
            ("flush_interval", "刷新间隔", str(self._flush_interval), str(rec["flush_interval"])),
        ]
        for key, label, current, default in items:
            ctk.CTkLabel(params_row, text=label, font=ctk.CTkFont(size=12), text_color=COLOR_TEXT).pack(side="left", padx=(0, 2))
            entry = ctk.CTkEntry(params_row, width=60, height=26, fg_color="#2a2a2a", border_color="#444",
                               text_color=COLOR_TEXT, font=ctk.CTkFont(size=12))
            entry.pack(side="left", padx=(0, 2))
            entry.insert(0, current)
            self._settings_entries[key] = entry
        btn_row = ctk.CTkFrame(self._settings_frame, fg_color="#252525")
        btn_row.pack(fill="x", padx=10, pady=(4, 8))

        def apply_rec():
            for key, _, _, default in items:
                self._settings_entries[key].delete(0, "end")
                self._settings_entries[key].insert(0, default)

        def save_inline():
            try:
                self._max_display = int(self._settings_entries["max_display"].get())
                self._max_depth = int(self._settings_entries["max_depth"].get())
                self._batch_size = int(self._settings_entries["batch_size"].get())
                self._flush_interval = float(self._settings_entries["flush_interval"].get())
                self.settings.update({"max_display": self._max_display, "max_depth": self._max_depth,
                                     "batch_size": self._batch_size, "flush_interval": self._flush_interval})
                save_settings(self.settings)
                self.toggle_settings_panel()
            except ValueError:
                messagebox.showerror("输入错误", "请输入有效的数值")

        ctk.CTkButton(btn_row, text="应用推荐值", height=26, fg_color="#333", hover_color=COLOR_RED,
                     text_color=COLOR_TEXT, font=ctk.CTkFont(size=12), command=apply_rec).pack(side="left", padx=(0, 5))
        ctk.CTkButton(btn_row, text="保存", height=26, fg_color=COLOR_RED, hover_color=COLOR_RED_LIGHT,
                     text_color=COLOR_TEXT, font=ctk.CTkFont(size=12), command=save_inline).pack(side="left", padx=5)

    def toggle_delete_settings_panel(self):
        self._close_other_panels("delete")
        if self._delete_settings_visible:
            if self._delete_settings_frame:
                self._delete_settings_frame.destroy()
                self._delete_settings_frame = None
            self._delete_settings_visible = False
            return
        self._delete_settings_visible = True
        self._delete_settings_frame = ctk.CTkFrame(self.cat_frame, fg_color="#252525", border_color="#444", border_width=1)
        self._delete_settings_frame.pack(fill="x", padx=10, pady=(0, 8))
        mode_row = ctk.CTkFrame(self._delete_settings_frame, fg_color="#252525")
        mode_row.pack(fill="x", padx=10, pady=(8, 4))
        ctk.CTkLabel(mode_row, text="删除方式", font=ctk.CTkFont(size=12, weight="bold"), text_color=COLOR_TEXT).pack(side="left", padx=(0, 10))
        self._delete_mode_var = ctk.StringVar(value=self.delete_mode)
        for val, label in [("permanent", "彻底删除"), ("recycle", "删除到回收站"), ("move", "移动到文件夹"), ("compress", "压缩为压缩包")]:
            ctk.CTkRadioButton(mode_row, text=label, variable=self._delete_mode_var, value=val,
                              fg_color=COLOR_RED, hover_color=COLOR_RED_LIGHT, text_color=COLOR_TEXT,
                              font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
        detail_row = ctk.CTkFrame(self._delete_settings_frame, fg_color="#252525")
        detail_row.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(detail_row, text="移动目录", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT).pack(side="left", padx=(0, 4))
        self._move_dir_entry = ctk.CTkEntry(detail_row, placeholder_text="选择移动目标文件夹...",
                                           fg_color="#2a2a2a", border_color="#444", text_color=COLOR_TEXT,
                                           placeholder_text_color=COLOR_DIM, height=26, font=ctk.CTkFont(size=12), width=300)
        self._move_dir_entry.pack(side="left", padx=(0, 4))
        self._move_dir_entry.insert(0, self.delete_move_dir)
        ctk.CTkButton(detail_row, text="浏览", width=50, height=26, command=self._browse_move_dir,
                     fg_color="#333", hover_color=COLOR_RED, text_color=COLOR_TEXT, font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 12))
        ctk.CTkLabel(detail_row, text="压缩包名", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT).pack(side="left", padx=(0, 4))
        self._zip_name_entry = ctk.CTkEntry(detail_row, placeholder_text="如 cleanup_{date}",
                                           fg_color="#2a2a2a", border_color="#444", text_color=COLOR_TEXT,
                                           placeholder_text_color=COLOR_DIM, height=26, font=ctk.CTkFont(size=12), width=180)
        self._zip_name_entry.pack(side="left", padx=(0, 4))
        self._zip_name_entry.insert(0, self.delete_zip_name)
        ctk.CTkLabel(detail_row, text="{date}=日期 {time}=时间", font=ctk.CTkFont(size=10), text_color=COLOR_DIM).pack(side="left")
        btn_row = ctk.CTkFrame(self._delete_settings_frame, fg_color="#252525")
        btn_row.pack(fill="x", padx=10, pady=(4, 8))

        def save_del():
            self.delete_mode = self._delete_mode_var.get()
            self.delete_move_dir = self._move_dir_entry.get().strip()
            self.delete_zip_name = self._zip_name_entry.get().strip() or "cleanup_{date}"
            self.settings.update({"delete_mode": self.delete_mode, "delete_move_dir": self.delete_move_dir,
                                 "delete_zip_name": self.delete_zip_name})
            save_settings(self.settings)
            self.toggle_delete_settings_panel()

        ctk.CTkButton(btn_row, text="保存", height=26, fg_color=COLOR_RED, hover_color=COLOR_RED_LIGHT,
                     text_color=COLOR_TEXT, font=ctk.CTkFont(size=12), command=save_del).pack(side="left", padx=5)

    def toggle_color_settings_panel(self):
        self._close_other_panels("color")
        if self._color_settings_visible:
            if self._color_settings_frame:
                self._color_settings_frame.destroy()
                self._color_settings_frame = None
            self._color_settings_visible = False
            return
        self._color_settings_visible = True
        self._color_settings_frame = ctk.CTkFrame(self.cat_frame, fg_color="#252525", border_color="#444", border_width=1)
        self._color_settings_frame.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkLabel(self._color_settings_frame, text="分类背景颜色", font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLOR_TEXT).pack(anchor="w", padx=10, pady=(8, 4))
        self._color_buttons = {}
        color_row = ctk.CTkFrame(self._color_settings_frame, fg_color="#252525")
        color_row.pack(fill="x", padx=10, pady=4)
        for cat_id, color in self.category_colors.items():
            name = CATEGORY_TREE.get(cat_id, {}).get("name", cat_id)
            item_frame = ctk.CTkFrame(color_row, fg_color="#252525")
            item_frame.pack(side="left", padx=3, pady=2)
            ctk.CTkLabel(item_frame, text=name, font=ctk.CTkFont(size=11), text_color=COLOR_TEXT).pack(side="left", padx=(0, 3))
            btn = ctk.CTkButton(item_frame, text="  ", width=28, height=20, fg_color=color, hover_color=color,
                              command=lambda cid=cat_id: self._pick_color(cid))
            btn.pack(side="left")
            self._color_buttons[cat_id] = btn
        btn_row = ctk.CTkFrame(self._color_settings_frame, fg_color="#252525")
        btn_row.pack(fill="x", padx=10, pady=(4, 8))

        def reset_c():
            self.category_colors = CATEGORY_COLORS_DEFAULT.copy()
            self.settings["category_colors"] = self.category_colors
            save_settings(self.settings)
            self._apply_tag_styles()
            self.display_files()
            self.toggle_color_settings_panel()

        def save_c():
            self.settings["category_colors"] = self.category_colors
            save_settings(self.settings)
            self._apply_tag_styles()
            self.display_files()
            self.toggle_color_settings_panel()

        ctk.CTkButton(btn_row, text="恢复默认", height=26, fg_color="#333", hover_color=COLOR_RED,
                     text_color=COLOR_TEXT, font=ctk.CTkFont(size=12), command=reset_c).pack(side="left", padx=(0, 5))
        ctk.CTkButton(btn_row, text="保存并应用", height=26, fg_color=COLOR_RED, hover_color=COLOR_RED_LIGHT,
                     text_color=COLOR_TEXT, font=ctk.CTkFont(size=12), command=save_c).pack(side="left", padx=5)

    def _pick_color(self, cat_id):
        current = self.category_colors.get(cat_id, COLOR_BG)
        result = colorchooser.askcolor(color=current, title="选择颜色")
        if result and result[1]:
            self.category_colors[cat_id] = result[1]
            if cat_id in self._color_buttons:
                self._color_buttons[cat_id].configure(fg_color=result[1], hover_color=result[1])

    def _apply_tag_styles(self):
        for cat_id, color in self.category_colors.items():
            tag_name = f"cat_{cat_id}"
            self.tree.tag_configure(tag_name, background=color, foreground=COLOR_TEXT)

    def _close_other_panels(self, keep):
        if keep != "settings" and self._settings_visible:
            self.toggle_settings_panel()
        if keep != "delete" and self._delete_settings_visible:
            self.toggle_delete_settings_panel()
        if keep != "color" and self._color_settings_visible:
            self.toggle_color_settings_panel()

    def _browse_move_dir(self):
        d = filedialog.askdirectory(title="选择移动目标文件夹")
        if d:
            self._move_dir_entry.delete(0, "end")
            self._move_dir_entry.insert(0, d)

    def setup_table_area(self):
        table_frame = ctk.CTkFrame(self.main_frame, fg_color=COLOR_BG, border_width=0)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(2, 0))

        tree_container = tk.Frame(table_frame, bg=COLOR_BG)
        tree_container.pack(fill="both", expand=True)

        self.scrollbar_y = ttk.Scrollbar(tree_container, orient="vertical", style="Dark.Vertical.TScrollbar")
        self.scrollbar_x = ttk.Scrollbar(tree_container, orient="horizontal", style="Dark.Horizontal.TScrollbar")

        columns = ("选择", "文件名", "完整路径", "大小", "修改时间", "类型", "分类")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15, style="Dark.Treeview",
                                yscrollcommand=self._on_yscroll, xscrollcommand=self._on_xscroll)
        self.tree.pack(side="left", fill="both", expand=True)

        self.scrollbar_y.configure(command=self.tree.yview)
        self.scrollbar_x.configure(command=self.tree.xview)

        self.tree.heading("选择", text="☑️全选", command=self.toggle_select_all)
        self.tree.heading("文件名", text="文件名 ▲▼", command=lambda: self.sort_by_column("文件名"))
        self.tree.heading("完整路径", text="完整路径 ▲▼", command=lambda: self.sort_by_column("完整路径"))
        self.tree.heading("大小", text="大小 ▲▼", command=lambda: self.sort_by_column("大小"))
        self.tree.heading("修改时间", text="修改时间 ▲▼", command=lambda: self.sort_by_column("修改时间"))
        self.tree.heading("类型", text="类型 ▲▼", command=lambda: self.sort_by_column("类型"))
        self.tree.heading("分类", text="分类 ▲▼", command=lambda: self.sort_by_column("分类"))

        for col in columns:
            w = self.column_widths.get(col, COLUMN_WIDTHS_DEFAULT.get(col, 100))
            mw = COLUMN_MIN_WIDTHS.get(col, 55)
            self.tree.column(col, width=w, minwidth=mw, stretch=True)

        self._snapshot_column_widths()

        for cat_id, color in self.category_colors.items():
            tag_name = f"cat_{cat_id}"
            text_color = CATEGORY_TEXT_COLORS.get(cat_id, COLOR_TEXT)
            self.tree.tag_configure(tag_name, background=color, foreground=text_color)

        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.tree.bind("<ButtonPress-1>", self._on_col_press)
        self.tree.bind("<ButtonRelease-1>", self._on_col_release)
        self.tree.bind("<Motion>", self._on_col_motion)

    def _on_yscroll(self, first, last):
        self.scrollbar_y.set(float(first), float(last))
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.scrollbar_y.pack_forget()
        else:
            if not self.scrollbar_y.winfo_ismapped():
                self.scrollbar_y.pack(side="right", fill="y", before=self.tree)

    def _on_xscroll(self, first, last):
        self.scrollbar_x.set(float(first), float(last))
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.scrollbar_x.pack_forget()
        else:
            if not self.scrollbar_y.winfo_ismapped():
                self.scrollbar_x.pack(side="bottom", fill="x", before=self.tree)
            else:
                self.scrollbar_x.pack(side="bottom", fill="x")

    def _snapshot_column_widths(self):
        self._prev_column_widths = {}
        try:
            for col in ("选择", "文件名", "完整路径", "大小", "修改时间", "类型", "分类"):
                self._prev_column_widths[col] = self.tree.column(col, "width")
        except Exception:
            pass

    def _on_col_press(self, event):
        self._snapshot_column_widths()

    def _on_col_motion(self, event):
        pass

    def _on_col_release(self, event):
        if not hasattr(self, 'tree'):
            return
        try:
            changed = False
            for col in ("选择", "文件名", "完整路径", "大小", "修改时间", "类型", "分类"):
                cur_w = self.tree.column(col, "width")
                prev_w = self._prev_column_widths.get(col, cur_w)
                if cur_w != prev_w:
                    changed = True
                    break
            if changed:
                self._save_column_widths()
        except Exception:
            pass

    def _save_column_widths(self):
        try:
            for col in ("选择", "文件名", "完整路径", "大小", "修改时间", "类型", "分类"):
                w = self.tree.column(col, "width")
                mw = COLUMN_MIN_WIDTHS.get(col, 55)
                self.column_widths[col] = max(w, mw)
            self.settings["column_widths"] = self.column_widths
        except Exception:
            pass

    def setup_status_bar(self):
        status_frame = ctk.CTkFrame(self.main_frame, fg_color=COLOR_BG, border_width=0)
        status_frame.pack(fill="x", padx=10, pady=(2, 4))
        status_info = ctk.CTkFrame(status_frame, fg_color=COLOR_BG)
        status_info.pack(fill="x", padx=5, pady=2)
        self.status_label = ctk.CTkLabel(status_info, text="✅ 准备就绪", anchor="w",
                                       font=ctk.CTkFont(weight="bold"), text_color=COLOR_TEXT)
        self.status_label.pack(side="left", fill="x", expand=True, padx=5)
        self.progress_label = ctk.CTkLabel(status_info, text="", anchor="e", font=ctk.CTkFont(size=12), text_color=COLOR_TEXT)
        self.progress_label.pack(side="right", padx=5)
        self.progress_bar = ctk.CTkProgressBar(status_frame, height=8, fg_color=COLOR_BORDER, progress_color=COLOR_RED)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 2))
        self.progress_bar.set(0)
        count_row = ctk.CTkFrame(status_frame, fg_color=COLOR_BG)
        count_row.pack(fill="x", padx=5, pady=2)
        self.count_label = ctk.CTkLabel(count_row, text="📊 文件: 0 | 总大小: 0 MB", anchor="w",
                                       text_color=COLOR_TEXT, font=ctk.CTkFont(size=12))
        self.count_label.pack(side="left", padx=5)
        self.selected_size_label = ctk.CTkLabel(count_row, text="☑ 已选: 0 个 | 已选大小: 0 MB", anchor="e",
                                               text_color=COLOR_RED_LIGHT, font=ctk.CTkFont(size=12, weight="bold"))
        self.selected_size_label.pack(side="right", padx=5)

    def _update_selected_size_display(self):
        count = len(self.selected_files)
        sel_size = 0
        all_sizes = {fi["path"]: fi["size"] for fi in self.file_list}
        for fp in self.selected_files:
            if fp in all_sizes:
                sel_size += all_sizes[fp]
        self.selected_size_label.configure(text=f"☑ 已选: {count} 个 | 已选大小: {round(sel_size / (1024*1024), 2)} MB")

    def browse_directory(self):
        d = filedialog.askdirectory(title="选择要扫描的目录")
        if d:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, d)
            self.settings["scan_directory"] = d
            save_settings(self.settings)

    def update_scan_conditions(self):
        self.scan_conditions = {}
        for cid, var in self.preset_vars.items():
            self.scan_conditions[cid] = var.get()

    def toggle_file_size_condition(self):
        if not self.size_enabled_var.get():
            self.file_size_condition = None
        else:
            self.update_file_size_condition()

    def update_file_size_condition(self):
        if self.size_enabled_var.get():
            try:
                self.file_size_condition = {
                    "operator": self.size_operator_var.get(),
                    "unit": self.size_unit_var.get(),
                    "value": float(self.size_value_entry.get())
                }
            except ValueError:
                pass

    def check_file_size_condition(self, file_size):
        if not self.file_size_condition:
            return True
        try:
            op = self.file_size_condition["operator"]
            unit = self.file_size_condition["unit"]
            val = self.file_size_condition["value"]
            sz = file_size
            if unit == "KB": sz /= 1024
            elif unit == "MB": sz /= (1024*1024)
            elif unit == "GB": sz /= (1024*1024*1024)
            if op == ">": return sz > val
            elif op == "<": return sz < val
        except Exception:
            return True
        return True

    def is_garbage_file(self, file_name, file_size, file_ext):
        if file_size < 1:
            return False, "", ""

        for cat_id, cat_info in CATEGORY_TREE.items():
            if "children" in cat_info:
                continue
            if not self.scan_conditions.get(cat_id, True):
                continue

            if "extensions" in cat_info and file_ext in cat_info["extensions"]:
                desc = cat_info["extensions"][file_ext]
                parent = cat_info.get("parent", "")
                parent_name = CATEGORY_TREE.get(parent, {}).get("name", cat_info["name"])
                return True, desc, parent_name if parent else cat_info["name"]

            if "system_files" in cat_info and file_name in cat_info["system_files"]:
                desc = cat_info["system_files"][file_name]
                parent = cat_info.get("parent", "")
                parent_name = CATEGORY_TREE.get(parent, {}).get("name", cat_info["name"])
                return True, desc, parent_name if parent else cat_info["name"]

            if "name_patterns" in cat_info:
                for pat, desc in cat_info["name_patterns"]:
                    if re.match(pat, file_name, re.IGNORECASE):
                        parent = cat_info.get("parent", "")
                        parent_name = CATEGORY_TREE.get(parent, {}).get("name", cat_info["name"])
                        return True, desc, parent_name if parent else cat_info["name"]

            if "image_patterns" in cat_info:
                fn_lower = file_name.lower()
                for pat in cat_info["image_patterns"]:
                    if re.match(pat, fn_lower, re.IGNORECASE):
                        parent = cat_info.get("parent", "")
                        parent_name = CATEGORY_TREE.get(parent, {}).get("name", cat_info["name"])
                        return True, "广告图片", parent_name if parent else cat_info["name"]

            if "link_patterns" in cat_info:
                fn_lower = file_name.lower()
                for pat in cat_info["link_patterns"]:
                    if re.match(pat, fn_lower, re.IGNORECASE):
                        parent = cat_info.get("parent", "")
                        parent_name = CATEGORY_TREE.get(parent, {}).get("name", cat_info["name"])
                        return True, "广告链接", parent_name if parent else cat_info["name"]

        custom_matches = []
        if self.custom_enabled_var.get():
            for rule in self.custom_rules:
                rt = rule.get("type", "suffix")
                rt_text = rule.get("text", "")
                if rt == "suffix" and file_ext == rt_text.lower():
                    custom_matches.append(rt_text)
                elif rt == "regex" and re.match(rt_text, file_name, re.IGNORECASE):
                    custom_matches.append(rt_text)
                elif rt == "name_fuzzy" and rt_text.lower() in file_name.lower():
                    custom_matches.append(rt_text)
                elif rt == "name_exact" and file_name == rt_text:
                    custom_matches.append(rt_text)

        if custom_matches:
            return True, f"自定义: {', '.join(custom_matches)}", "自定义规则"
        return False, "", ""

    def _fast_scan_dir(self, directory):
        subdirs = []
        try:
            with os.scandir(directory) as it:
                for entry in it:
                    if self.scan_cancelled:
                        return subdirs
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            subdirs.append(entry)
                        elif entry.is_file(follow_symlinks=False):
                            try:
                                st = entry.stat(follow_symlinks=False)
                                fn = entry.name
                                fe = os.path.splitext(fn)[1].lower()
                                ok, desc, cat = self.is_garbage_file(fn, st.st_size, fe)
                                if ok and self.check_file_size_condition(st.st_size):
                                    self._add_file_realtime({
                                        "path": entry.path, "name": fn, "size": st.st_size,
                                        "mtime": st.st_mtime, "type": fe, "category": cat, "desc": desc
                                    })
                            except Exception:
                                pass
                    except Exception:
                        continue
        except Exception:
            pass
        return subdirs

    def _add_file_realtime(self, info):
        self.file_list.append(info)
        self.total_size += info["size"]
        self.processed_items += 1
        days = int(self.days_var.get())
        if days > 0:
            cutoff = datetime.now() - timedelta(days=days)
            if datetime.fromtimestamp(info["mtime"]) >= cutoff:
                return
        self.filtered_files.append(info)
        if self._displayed_count < self._max_display:
            self._pending_ui_updates.append(info)
            self._displayed_count += 1
        now = time.monotonic()
        if len(self._pending_ui_updates) >= self._batch_size or (now - self._last_ui_flush > self._flush_interval and self._pending_ui_updates):
            self._last_ui_flush = now
            self._flush_ui_updates()

    def _flush_ui_updates(self):
        if not self._pending_ui_updates:
            return
        updates = self._pending_ui_updates[:]
        self._pending_ui_updates.clear()
        self.root.after(0, lambda: self._do_ui_insert(updates))

    def _get_cat_tag(self, category):
        key = CATEGORY_TO_CHECKBOX.get(category, "")
        return f"cat_{key}" if key else ""

    def _do_ui_insert(self, file_infos):
        for fi in file_infos:
            fp = fi["path"]
            cat_key = CATEGORY_TO_CHECKBOX.get(fi["category"], "")
            is_sel = cat_key and self.preset_vars.get(cat_key, self.custom_enabled_var if cat_key == "custom" else None)
            if isinstance(is_sel, ctk.BooleanVar):
                is_sel = is_sel.get()
            else:
                is_sel = fp in self.selected_files
            if is_sel:
                self.selected_files.add(fp)
            tag = self._get_cat_tag(fi["category"])
            tags = (tag, fp) if tag else (fp,)
            self.tree.insert("", "end",
                           values=("☑" if is_sel else "☐", fi["name"], fp,
                                  self.format_size(fi["size"]),
                                  datetime.fromtimestamp(fi["mtime"]).strftime("%Y-%m-%d %H:%M:%S"),
                                  fi["type"], fi["category"]),
                           tags=tags)
        tf = len(self.filtered_files)
        tsm = round(self.total_size / (1024*1024), 2)
        self.count_label.configure(text=f"📊 文件: {tf} | 总大小: {tsm} MB" + (f" (显示前{self._max_display}条)" if tf > self._max_display else ""))
        self._update_selected_size_display()
        self._auto_save_results()

    def _scan_worker(self, directory):
        if self._scan_depth >= self._max_depth:
            return
        self._scan_depth += 1
        try:
            subdirs = self._fast_scan_dir(directory)
            for entry in subdirs:
                if self.scan_cancelled:
                    return
                if self.scan_conditions.get("empty_folders", True):
                    try:
                        empty = True
                        with os.scandir(entry.path) as si:
                            for se in si:
                                empty = False
                                break
                        if empty:
                            st = entry.stat(follow_symlinks=False)
                            self._add_file_realtime({
                                "path": entry.path, "name": entry.name, "size": 0,
                                "mtime": st.st_mtime, "type": "文件夹", "category": "空文件夹", "desc": "空文件夹"
                            })
                    except Exception:
                        pass
                self._scan_worker(entry.path)
        finally:
            self._scan_depth -= 1

    def start_scan(self):
        directory = self.dir_entry.get().strip()
        if not directory or not os.path.isdir(directory):
            messagebox.showwarning("输入错误", "请选择有效的扫描目录")
            return
        self.file_list.clear()
        self.filtered_files.clear()
        self.selected_files.clear()
        self._pending_ui_updates.clear()
        self.total_size = 0
        self.processed_items = 0
        self._displayed_count = 0
        self._scan_depth = 0
        self.clear_table()
        self.status_label.configure(text="🔍 正在快速扫描...")
        self.progress_bar.set(0)
        self.count_label.configure(text="📊 文件: 0 | 总大小: 0 MB")
        self.selected_size_label.configure(text="☑ 已选: 0 个 | 已选大小: 0 MB")
        self.stop_button.configure(state="normal")
        self.scanning = True
        self.scan_cancelled = False
        self.settings["scan_directory"] = directory
        self.settings["last_scan_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_settings(self.settings)
        threading.Thread(target=self.run_scan, args=(directory,), daemon=True).start()

    def start_duplicate_scan(self):
        if not self.file_list:
            messagebox.showwarning("提示", "请先执行扫描")
            return
        if self.scanning:
            messagebox.showwarning("提示", "请等待扫描完成")
            return
        self.scan_cancelled = False
        self.stop_button.configure(state="normal")
        threading.Thread(target=self._run_dup_scan, daemon=True).start()

    def _run_dup_scan(self):
        try:
            self._detect_duplicates()
            if not self.scan_cancelled:
                self._flush_ui_updates()
                self.root.after(0, lambda: self.status_label.configure(text="✅ 重复文件检测完成"))
        except Exception:
            self.root.after(0, lambda: self.status_label.configure(text="❌ 重复检测出错"))
        finally:
            self._flush_ui_updates()
            self.root.after(0, lambda: self.stop_button.configure(state="disabled"))
            self.root.after(0, lambda: self.progress_bar.set(1.0))

    def _detect_duplicates(self):
        self.root.after(0, lambda: self.status_label.configure(text="🔍 正在比对重复文件..."))
        size_groups = {}
        for f in self.file_list:
            if f["size"] > 0 and f["category"] != "空文件夹":
                size_groups.setdefault(f["size"], []).append(f)
        existing = {f["path"] for f in self.file_list}
        for sz, files in size_groups.items():
            if len(files) < 2 or self.scan_cancelled:
                continue
            head_groups = {}
            for fi in files:
                if self.scan_cancelled: return
                h = self._head_hash(fi["path"])
                if h: head_groups.setdefault(h, []).append(fi)
            for h, cands in head_groups.items():
                if len(cands) < 2 or self.scan_cancelled: continue
                full_groups = {}
                for fi in cands:
                    if self.scan_cancelled: return
                    fh = self._full_hash(fi["path"])
                    if fh: full_groups.setdefault(fh, []).append(fi)
                for fh, group in full_groups.items():
                    if len(group) < 2: continue
                    group.sort(key=lambda x: x["mtime"])
                    for fi in group[1:]:
                        if fi["path"] not in existing:
                            self._add_file_realtime({
                                "path": fi["path"], "name": fi["name"], "size": fi["size"],
                                "mtime": fi["mtime"], "type": fi["type"], "category": "重复文件",
                                "desc": f"与 {group[0]['name']} 重复"
                            })
                            existing.add(fi["path"])

    def _head_hash(self, fp, hs=4096):
        try:
            h = hashlib.md5()
            with open(fp, 'rb') as f: h.update(f.read(hs))
            return h.hexdigest()
        except Exception:
            return None

    def _full_hash(self, fp, cs=65536):
        try:
            h = hashlib.md5()
            with open(fp, 'rb') as f:
                while True:
                    c = f.read(cs)
                    if not c: break
                    h.update(c)
            return h.hexdigest()
        except Exception:
            return None

    def run_scan(self, directory):
        try:
            self._scan_worker(directory)
            if not self.scan_cancelled:
                self._flush_ui_updates()
                self.root.after(0, lambda: self.status_label.configure(text="✅ 扫描完成"))
        except Exception:
            self.root.after(0, lambda: self.status_label.configure(text="❌ 扫描出错"))
        finally:
            self._flush_ui_updates()
            self.scanning = False
            self.root.after(0, lambda: self.stop_button.configure(state="disabled"))
            self.root.after(0, lambda: self.progress_bar.set(1.0))
            self._auto_save_results()

    def stop_scan(self):
        self.scan_cancelled = True
        self.status_label.configure(text="⏹️ 扫描已停止")

    def display_files(self):
        self.clear_table()
        for fi in self.filtered_files:
            fp = fi["path"]
            cat_key = CATEGORY_TO_CHECKBOX.get(fi["category"], "")
            is_sel = cat_key and self.preset_vars.get(cat_key, self.custom_enabled_var if cat_key == "custom" else None)
            if isinstance(is_sel, ctk.BooleanVar):
                is_sel = is_sel.get()
            else:
                is_sel = fp in self.selected_files
            tag = self._get_cat_tag(fi["category"])
            tags = (tag, fp) if tag else (fp,)
            self.tree.insert("", "end",
                           values=("☑" if is_sel else "☐", fi["name"], fp,
                                  self.format_size(fi["size"]),
                                  datetime.fromtimestamp(fi["mtime"]).strftime("%Y-%m-%d %H:%M:%S"),
                                  fi["type"], fi["category"]),
                           tags=tags)
        tf = len(self.filtered_files)
        tsm = round(self.total_size / (1024*1024), 2)
        self.count_label.configure(text=f"📊 文件: {tf} | 总大小: {tsm} MB")
        self._update_selected_size_display()

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def format_size(self, sb):
        if sb == 0: return "0 B"
        names = ['B', 'KB', 'MB', 'GB', 'TB']
        i = 0
        while sb >= 1024 and i < len(names) - 1:
            sb /= 1024; i += 1
        return f"{round(sb, 2)} {names[i]}"

    def toggle_select_all(self):
        sa = not self.select_all_var.get()
        self.select_all_var.set(sa)
        self.selected_files.clear()
        if sa:
            for fi in self.filtered_files:
                self.selected_files.add(fi["path"])
        for item in self.tree.get_children():
            fp = self.tree.item(item, "tags")[0]
            self.tree.item(item, values=("☑" if fp in self.selected_files else "☐", *self.tree.item(item, "values")[1:]))
        self._update_selected_size_display()

    def on_item_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            fp = self.tree.item(item, "tags")[0]
            if fp in self.selected_files:
                self.selected_files.remove(fp)
            else:
                self.selected_files.add(fp)
            self.tree.item(item, values=("☑" if fp in self.selected_files else "☐", *self.tree.item(item, "values")[1:]))
            self._update_selected_size_display()

    def add_custom_rule(self):
        text = self.custom_rule_entry.get().strip()
        if not text:
            return
        rtype = self.custom_rule_type_var.get()
        if rtype == "suffix" and not text.startswith('.'):
            text = '.' + text
        elif rtype == "regex":
            try: re.compile(text)
            except re.error:
                messagebox.showerror("错误", f"'{text}' 不是有效的正则表达式")
                return
        rule = {"text": text, "type": rtype}
        self.custom_rules.append(rule)
        self.custom_rule_entry.delete(0, "end")
        self._rebuild_rules_display()
        self._auto_save()

    def _rebuild_rules_display(self):
        for w in self.rules_list_frame.winfo_children():
            w.destroy()
        labels = {"suffix": "后缀", "regex": "正则", "name_fuzzy": "模糊名", "name_exact": "精确名"}
        for rule in self.custom_rules:
            rf = ctk.CTkFrame(self.rules_list_frame, fg_color=COLOR_BG, border_color=COLOR_BORDER, border_width=1)
            rf.pack(fill="x", padx=2, pady=2)
            ctk.CTkLabel(rf, text=f"{rule['text']} [{labels.get(rule['type'], '')}]",
                        font=ctk.CTkFont(size=12), text_color=COLOR_TEXT).pack(side="left", padx=5, pady=2)
            ctk.CTkButton(rf, text="删除", width=60, command=lambda r=rule: self.remove_custom_rule(r),
                         fg_color=COLOR_RED, hover_color=COLOR_RED_LIGHT, border_color=COLOR_BORDER, border_width=1).pack(side="right", padx=5, pady=2)

    def remove_custom_rule(self, rule):
        if rule in self.custom_rules:
            self.custom_rules.remove(rule)
        self._rebuild_rules_display()
        self._auto_save()

    def clear_custom_rules(self):
        self.custom_rules.clear()
        self._rebuild_rules_display()
        self._auto_save()

    def verify_results(self):
        if not self.file_list:
            messagebox.showwarning("提示", "没有扫描结果")
            return
        self.status_label.configure(text="✅ 正在校验...")
        removed = changed = 0
        valid = []
        for fi in self.file_list:
            fp = fi["path"]
            if not os.path.exists(fp):
                removed += 1
                self.selected_files.discard(fp)
                continue
            try:
                st = os.stat(fp)
                if st.st_size != fi["size"] or st.st_mtime != fi["mtime"]:
                    fi["size"] = st.st_size
                    fi["mtime"] = st.st_mtime
                    changed += 1
            except Exception:
                removed += 1
                self.selected_files.discard(fp)
                continue
            valid.append(fi)
        self.file_list = valid
        self.filtered_files = valid[:]
        self.total_size = sum(fi["size"] for fi in valid)
        self.display_files()
        self._auto_save_results()
        self.status_label.configure(text=f"✅ 校验完成 | 有效:{len(valid)} 删除:{removed} 变更:{changed}")
        messagebox.showinfo("校验结果", f"有效: {len(valid)}\n已删除: {removed}\n已变更: {changed}")

    def _auto_save(self):
        cat_enabled = {cid: var.get() for cid, var in self.preset_vars.items()}
        self.settings["category_enabled"] = cat_enabled
        self.settings["custom_rules"] = self.custom_rules
        self.settings["custom_enabled"] = self.custom_enabled_var.get()
        self.settings["size_enabled"] = self.size_enabled_var.get()
        self.settings["size_operator"] = self.size_operator_var.get()
        self.settings["size_value"] = self.size_value_entry.get()
        self.settings["size_unit"] = self.size_unit_var.get()
        self.settings["days_value"] = self.days_var.get()
        self.settings["mode_value"] = self.mode_var.get()
        self._save_column_widths()
        self.settings["delete_mode"] = self.delete_mode
        self.settings["delete_move_dir"] = self.delete_move_dir
        self.settings["delete_zip_name"] = self.delete_zip_name
        self.settings["category_colors"] = self.category_colors
        self.settings["scan_directory"] = self.dir_entry.get().strip()
        save_settings(self.settings)

    def _auto_save_results(self):
        data = {
            "scan_directory": self.dir_entry.get().strip(),
            "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_size": self.total_size,
            "selected_files": list(self.selected_files),
            "file_list": [{"path": fi["path"], "name": fi["name"], "size": fi["size"],
                          "mtime": fi["mtime"], "type": fi["type"], "category": fi["category"], "desc": fi["desc"]}
                         for fi in self.file_list],
        }
        save_scan_results(data)

    def _try_restore_results(self):
        data = load_scan_results()
        if not data: return
        saved = data.get("file_list", [])
        if not saved: return
        valid = [fi for fi in saved if os.path.exists(fi.get("path", ""))]
        if not valid: return
        self.file_list = valid
        self.filtered_files = valid[:]
        self.total_size = data.get("total_size", sum(fi["size"] for fi in valid))
        self.selected_files = set(data.get("selected_files", [])) & {fi["path"] for fi in valid}
        sd = data.get("scan_directory", "")
        if sd:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, sd)
        self.display_files()
        self.status_label.configure(text=f"📂 已恢复上次结果 ({data.get('scan_time', '')}) | 点击 ✅校验结果 验证")

    def delete_selected_files(self):
        if not self.selected_files:
            messagebox.showwarning("提示", "请先选择文件")
            return
        mode = self.delete_mode
        mn = {"permanent": "彻底删除", "recycle": "删除到回收站", "move": f"移动到 {self.delete_move_dir}", "compress": f"压缩为 {self._get_zip_name()}"}
        if not messagebox.askyesno("确认", f"处理 {len(self.selected_files)} 个文件？\n方式: {mn.get(mode, '彻底删除')}"):
            return
        ok = fail = 0
        to_compress = []
        for fp in list(self.selected_files):
            try:
                if os.path.isfile(fp):
                    sz = os.path.getsize(fp)
                    if mode == "permanent": os.remove(fp)
                    elif mode == "recycle": self._recycle(fp)
                    elif mode == "move": self._move(fp)
                    elif mode == "compress": to_compress.append(fp); continue
                elif os.path.isdir(fp):
                    if mode == "permanent": os.rmdir(fp)
                    elif mode == "recycle": self._recycle(fp)
                    elif mode == "move": self._move(fp)
                    elif mode == "compress": to_compress.append(fp); continue
                else:
                    continue
                ok += 1
                self.total_size -= sz if os.path.isfile(fp) else 0
                self.selected_files.discard(fp)
                self.file_list = [f for f in self.file_list if f["path"] != fp]
                self.filtered_files = [f for f in self.filtered_files if f["path"] != fp]
                for item in self.tree.get_children():
                    if self.tree.item(item, "tags")[0] == fp:
                        self.tree.delete(item); break
            except Exception:
                fail += 1
        if mode == "compress" and to_compress:
            if self._compress(to_compress, self._get_zip_name()):
                for fp in to_compress:
                    try:
                        sz = os.path.getsize(fp) if os.path.isfile(fp) else 0
                        os.remove(fp); ok += 1; self.total_size -= sz
                        self.selected_files.discard(fp)
                        self.file_list = [f for f in self.file_list if f["path"] != fp]
                        self.filtered_files = [f for f in self.filtered_files if f["path"] != fp]
                        for item in self.tree.get_children():
                            if self.tree.item(item, "tags")[0] == fp: self.tree.delete(item); break
                    except Exception:
                        fail += 1
            else:
                fail += len(to_compress)
        self._auto_save_results()
        messagebox.showinfo("完成", f"成功: {ok}\n失败: {fail}")
        tf = len(self.filtered_files)
        tsm = round(self.total_size / (1024*1024), 2)
        self.count_label.configure(text=f"📊 文件: {tf} | 总大小: {tsm} MB")
        self._update_selected_size_display()

    def _get_zip_name(self):
        n = self.delete_zip_name
        now = datetime.now()
        return n.replace("{date}", now.strftime("%Y%m%d")).replace("{time}", now.strftime("%H%M%S"))

    def _recycle(self, fp):
        try:
            import ctypes
            buf = ctypes.create_unicode_buffer(fp)
            ctypes.windll.shell32.SHFileOperationW(None, 0x1000 | 0x3, buf, None, 0x2 | 0x4, None, None)
        except Exception:
            if os.path.isfile(fp): os.remove(fp)
            elif os.path.isdir(fp): shutil.rmtree(fp)

    def _move(self, fp):
        td = self.delete_move_dir or os.path.join(get_base_dir(), "deleted_files")
        os.makedirs(td, exist_ok=True)
        tp = os.path.join(td, os.path.basename(fp))
        if os.path.exists(tp):
            n, e = os.path.splitext(os.path.basename(fp))
            tp = os.path.join(td, f"{n}_{int(time.time())}{e}")
        shutil.move(fp, tp)

    def _compress(self, fps, zn):
        try:
            td = self.delete_move_dir or get_base_dir()
            os.makedirs(td, exist_ok=True)
            zp = os.path.join(td, f"{zn}.zip")
            with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as zf:
                for fp in fps:
                    if os.path.isfile(fp): zf.write(fp, os.path.basename(fp))
                    elif os.path.isdir(fp):
                        for root, dirs, files in os.walk(fp):
                            for f in files:
                                full = os.path.join(root, f)
                                zf.write(full, os.path.relpath(full, os.path.dirname(fp)))
            return True
        except Exception:
            return False

    def sort_by_column(self, col):
        if self.sort_column == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False
        if col == "大小":
            self.filtered_files.sort(key=lambda x: x["size"], reverse=self.sort_reverse)
        elif col == "修改时间":
            self.filtered_files.sort(key=lambda x: x["mtime"], reverse=self.sort_reverse)
        else:
            self.filtered_files.sort(key=lambda x: x.get(col, ""), reverse=self.sort_reverse)
        self.display_files()


def main():
    app = GarbageCleanupTool()
    app.root.mainloop()


if __name__ == "__main__":
    main()
