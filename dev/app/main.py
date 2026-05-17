#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

if getattr(sys, 'frozen', False):
    base = sys._MEIPASS
    tcl_dir = os.path.join(base, 'tcl', 'tcl8.6')
    tk_dir = os.path.join(base, 'tk', 'tk8.6')
    if os.path.isdir(tcl_dir):
        os.environ['TCL_LIBRARY'] = tcl_dir
    if os.path.isdir(tk_dir):
        os.environ['TK_LIBRARY'] = tk_dir

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
from PIL import Image, ImageTk
import json
import hashlib
import threading
from datetime import datetime, timedelta
import time
import re
import psutil
import shutil
import zipfile
import io
import math

HAS_MATPLOTLIB = False
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_MATPLOTLIB = True
except Exception:
    pass

VERSION = "DEV"
VERSION_CHECK_URL = ""
APP_NAME = f"云集智能文件清理专家 v{VERSION}"

COLOR_RED = "#CC0000"
COLOR_RED_LIGHT = "#FF0000"
COLOR_BG = "#1a1a1a"
COLOR_BORDER = "#333333"
COLOR_TEXT = "#ffffff"
COLOR_DIM = "#888888"

FONT_FAMILY = "Microsoft YaHei UI"
FONT_FAMILY_MONO = "Consolas"

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
    "选择": 20, "文件名": 120, "完整路径": 500,
    "大小": 70, "修改时间": 130, "类型": 60, "分类": 80,
}

COLUMN_MIN_WIDTHS = {
    "选择": 20, "文件名": 60, "完整路径": 150,
    "大小": 55, "修改时间": 110, "类型": 40, "分类": 50,
}

PRESET_RULE_PACKS = {
    "windows_basic": {
        "name": "Windows基础清理",
        "desc": "系统临时文件、更新缓存、错误报告",
        "categories": ["temp", "cache", "crash_dump", "empty_folders"],
        "extensions": {".tmp": "系统临时文件", ".temp": "临时文件", ".log": "日志文件",
                       ".bak": "备份文件", ".old": "旧文件", ".dmp": "内存转储",
                       ".crash": "崩溃报告", ".cache": "缓存文件", ".thumb": "缩略图缓存"},
    },
    "windows_deep": {
        "name": "Windows深度清理",
        "desc": "基础清理+数据库缓存、索引文件、崩溃转储",
        "categories": ["temp", "cache", "db_cache", "data_file", "crash_dump", "empty_folders"],
        "extensions": {".tmp": "系统临时文件", ".temp": "临时文件", ".log": "日志文件",
                       ".bak": "备份文件", ".old": "旧文件", ".db": "数据库缓存",
                       ".sqlite": "SQLite缓存", ".sqlite3": "SQLite缓存", ".dat": "数据文件",
                       ".idx": "索引文件", ".dmp": "内存转储", ".crash": "崩溃报告",
                       ".cache": "缓存文件", ".thumb": "缩略图缓存", ".thumbnail": "缩略图",
                       "Thumbs.db": "系统缩略图缓存", "Desktop.ini": "桌面配置文件",
                       "iconcache.db": "图标缓存"},
    },
    "browser_cache": {
        "name": "浏览器缓存清理",
        "desc": "Chrome/Edge/Firefox等浏览器缓存、Cookie、历史记录",
        "categories": ["sys_cache", "db_cache"],
        "extensions": {".cache": "浏览器缓存", ".sqlite": "浏览器数据库", ".sqlite3": "浏览器数据",
                       ".db": "浏览器缓存", ".log": "浏览器日志"},
        "system_files": {"Web Data": "浏览器数据", "History": "浏览历史",
                        "Cookies": "Cookie文件", "Local Storage": "本地存储"},
    },
    "download_cleaner": {
        "name": "下载工具清理",
        "desc": "迅雷/浏览器/电驴等下载工具临时文件和链接",
        "categories": ["download_group", "thunder", "browser_dl", "dl_links", "emule_tmp"],
        "extensions": {".td": "迅雷未完成", ".ttd": "迅雷临时", ".xltd": "迅雷极速版",
                       ".torrent": "种子文件", ".magnet": "磁链文件", ".download": "浏览器下载",
                       ".crdownload": "Chrome下载", ".part": "部分下载",
                       ".part.met": "电驴元数据", ".met": "电驴元数据"},
    },
    "dev_tools": {
        "name": "开发者工具清理",
        "desc": "IDE缓存、Node_modules、Python缓存、编译临时文件",
        "categories": ["temp", "cache", "db_cache"],
        "extensions": {".pyc": "Python编译", ".pyo": "Python优化", ".class": "Java编译",
                       ".o": "C/C++目标文件", ".obj": "编译目标", ".log": "构建日志",
                       ".cache": "工具缓存", ".tmp": "临时文件"},
        "name_patterns": [(r'^__pycache__$', 'Python缓存'), (r'^node_modules$', 'Node模块')],
    },
    "ad_tracker": {
        "name": "广告追踪清理",
        "desc": "广告脚本、追踪数据、广告图片和链接",
        "categories": ["ads", "ad_file", "track_data", "ad_image", "ad_link"],
        "extensions": {".ad": "广告文件", ".ads": "广告脚本", ".tracking": "追踪文件",
                       ".analytics": "分析数据", ".metrics": "度量数据"},
        "image_patterns": [r'.*banner.*\.(jpg|jpeg|png|gif|webp|bmp|svg)$',
                          r'.*ad[_\-].*\.(jpg|jpeg|png|gif|webp|bmp|svg)$',
                          r'.*promo.*\.(jpg|jpeg|png|gif|webp|bmp|svg)$'],
    },
    "game_temp": {
        "name": "游戏临时文件",
        "desc": "游戏缓存、着色器缓存、游戏日志",
        "categories": ["temp", "cache"],
        "extensions": {".tmp": "游戏临时文件", ".cache": "游戏缓存", ".log": "游戏日志",
                       ".shadercache": "着色器缓存", ".loc": "本地化缓存"},
        "name_patterns": [(r'.*shader.?cache.*', '着色器缓存'),
                         (r'.*unreal.?engine.*temp.*', 'UE临时文件')],
    },
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
                        font=("Microsoft YaHei UI", 11), padx=6, pady=4)
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
        self.root.minsize(900, 600)
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.file_list = []
        self.filtered_files = []
        self.total_size = 0

        self.scanning = False
        self.scan_cancelled = False
        self.scan_paused = False
        self.processed_items = 0

        self.scan_conditions = {}
        self.custom_rules = []
        self.condition_mode = "stacked"
        self.file_size_condition = None

        self.sort_column = None
        self.sort_reverse = False
        self.selected_files = set()
        self.selected_size = 0
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
        self._batch_size = self.settings.get("batch_size", 50)
        self._flush_interval = self.settings.get("flush_interval", 0.3)
        self._file_size_map = {}
        self._last_auto_save_time = 0.0
        self._auto_save_interval = 5.0

        self._current_panel = None
        self._current_panel_type = None
        self._dup_groups = []

        self.preset_vars = {}
        self._prev_column_widths = {}
        self._cat_rows = []
        self._cat_child_rows = {}
        self._cat_color_btns = {}
        self._cat_tag_frames = {}
        self._cat_tag_labels = {}
        self._child_checkboxes = {}
        self._parent_checkboxes = {}
        self._cat_toggle_btns = {}
        self._cat_expanded = False
        self._active_rule_packs = set(self.settings.get("active_rule_packs", ["windows_basic"]))
        self._chart_images = {}
        self._chart_labels = {}

        for rule_id, rule_data in self.settings.get("custom_rule_packs", {}).items():
            PRESET_RULE_PACKS[rule_id] = rule_data

        self.setup_ui()
        self._set_icon()

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
                       font=('Microsoft YaHei UI', 12), rowheight=32, relief="flat",
                       bordercolor=COLOR_BG, lightcolor=COLOR_BG, darkcolor=COLOR_BG)
        style.configure("Dark.Treeview.Heading",
                       background="#252525", foreground=COLOR_TEXT,
                       borderwidth=0, relief="flat",
                       font=('Microsoft YaHei UI', 12, 'bold'),
                       bordercolor="#252525", lightcolor="#252525", darkcolor="#252525")
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

        self.main_frame = ctk.CTkFrame(self.root, fg_color=COLOR_BG, border_color=COLOR_BORDER, border_width=2)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.setup_status_bar()
        self.setup_scan_conditions()
        self.setup_control_panel()
        self.setup_table_area()

    def _make_color_tag(self, parent, text, cat_id, variable, command, font_size=12):
        color = self.category_colors.get(cat_id, COLOR_BG)
        tag_frame = ctk.CTkFrame(parent, fg_color=color, corner_radius=6)
        tag_frame.pack(side="left", padx=(2, 4), pady=2)

        cb = ctk.CTkCheckBox(tag_frame, text=text, variable=variable, command=command,
                            fg_color=COLOR_RED, hover_color=COLOR_RED_LIGHT,
                            checkmark_color=COLOR_TEXT, text_color=COLOR_TEXT,
                            font=ctk.CTkFont(family=FONT_FAMILY, size=font_size), corner_radius=4,
                            bg_color=color, border_width=0)
        cb.pack(padx=4, pady=2)

        tooltip_text = CATEGORY_TREE.get(cat_id, {}).get("tooltip", "")
        if tooltip_text:
            ToolTip(cb, tooltip_text)
            ToolTip(tag_frame, tooltip_text)

        return tag_frame, cb

    def _create_cat_tag_row(self, parent, cat_id, cat_info, var, command,
                            font_size=12, height=24, parent_color=None):
        bg_color = parent_color if parent_color else self.category_colors.get(cat_id, COLOR_BG)
        text_color = CATEGORY_TEXT_COLORS.get(cat_id, COLOR_TEXT) if parent_color else COLOR_TEXT

        tag_frame = ctk.CTkFrame(parent, fg_color=bg_color, corner_radius=4)
        tag_frame.pack(side="left", padx=(0, 0), pady=0)
        self._cat_tag_frames[cat_id] = tag_frame

        cb = ctk.CTkCheckBox(tag_frame, text=cat_info["name"], variable=var, command=command,
                            fg_color=COLOR_RED, hover_color=COLOR_RED_LIGHT,
                            checkmark_color=text_color, text_color=text_color,
                            font=ctk.CTkFont(family=FONT_FAMILY, size=font_size), corner_radius=4,
                            bg_color=bg_color, border_width=0, height=height)
        cb.pack(side="left", padx=4, pady=(2 if height >= 24 else 1))

        tooltip_text = cat_info.get("tooltip", "")
        if tooltip_text:
            ToolTip(cb, tooltip_text)
            ToolTip(tag_frame, tooltip_text)

        color_btn = ctk.CTkButton(parent, text="调色", width=28, height=height, fg_color="#444", hover_color="#555",
                                 text_color=COLOR_DIM, font=ctk.CTkFont(family=FONT_FAMILY, size=9),
                                 command=lambda cid=cat_id: self._pick_color_inline(cid))
        color_btn.pack(side="left", padx=(2, 0))
        self._cat_color_btns[cat_id] = color_btn

        return tag_frame, cb, color_btn

    def setup_control_panel(self):
        control_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e1e1e", border_color=COLOR_BORDER, border_width=1)
        control_frame.pack(fill="x", padx=10, pady=(5, 2))

        ctk.CTkLabel(control_frame, text="📁", font=ctk.CTkFont(family=FONT_FAMILY, size=16)).pack(side="left", padx=(10, 3))

        self.dir_entry = ctk.CTkEntry(control_frame, placeholder_text="选择要扫描的目录...",
                                     fg_color="#2a2a2a", border_color="#444",
                                     text_color=COLOR_TEXT, placeholder_text_color=COLOR_DIM, height=34)
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=3, pady=8)
        if self.settings.get("scan_directory"):
            self.dir_entry.insert(0, self.settings["scan_directory"])

        ctk.CTkButton(control_frame, text="浏览", width=60, height=34, command=self.browse_directory,
                     fg_color="#333", hover_color=COLOR_RED, text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=13)).pack(side="left", padx=3)
        self.scan_btn = ctk.CTkButton(control_frame, text="🔍 开始扫描", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), height=34,
                     fg_color=COLOR_RED, hover_color=COLOR_RED_LIGHT, command=self.start_scan)
        self.scan_btn.pack(side="left", padx=3)
        self.pause_btn = ctk.CTkButton(control_frame, text="⏸ 暂停", height=34, command=self.pause_scan,
                                        fg_color="#333", hover_color="#555", text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        self.cancel_btn = ctk.CTkButton(control_frame, text="✕ 取消", height=34, command=self.cancel_scan,
                                         fg_color="#333", hover_color=COLOR_RED, text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=13))
        ctk.CTkButton(control_frame, text="🔍 重复检测", height=34, command=self.start_duplicate_scan,
                     fg_color="#333", hover_color=COLOR_RED, text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=13)).pack(side="left", padx=3)
        ctk.CTkButton(control_frame, text="🗑️ 删除选中", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"), height=34,
                     fg_color=COLOR_RED, hover_color=COLOR_RED_LIGHT, command=self.delete_selected_files).pack(side="right", padx=(3, 10))
        self._update_scan_button_state("idle")

    def setup_scan_conditions(self):
        saved_enabled = self.settings.get("category_enabled", {})

        self._func_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e1e1e", border_color=COLOR_BORDER, border_width=1)
        self._func_frame.pack(fill="x", padx=10, pady=(10, 2))

        func_row = ctk.CTkFrame(self._func_frame, fg_color="#1e1e1e")
        func_row.pack(fill="x", padx=8, pady=6)

        ctk.CTkLabel(func_row, text="功能设置", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                    text_color=COLOR_DIM).pack(side="left", padx=(0, 8))

        func_buttons = [
            ("📋 预设规则", self.toggle_preset_rules_panel),
            ("⚙ 扫描设置", self.toggle_settings_panel),
            ("🗑 删除设置", self.toggle_delete_settings_panel),
            ("📊 分析报告", self.toggle_analysis_report),
            ("🔄 软件更新", self.toggle_version_panel),
        ]
        for text, cmd in func_buttons:
            ctk.CTkButton(func_row, text=text, height=26, fg_color="#333", hover_color=COLOR_RED,
                         text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=12), command=cmd).pack(side="left", padx=10)

        self.cat_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e1e1e", border_color=COLOR_BORDER, border_width=1)
        self.cat_frame.pack(fill="x", padx=10, pady=2)

        self._cat_grid = ctk.CTkFrame(self.cat_frame, fg_color="#1e1e1e")
        self._cat_grid.pack(fill="x", padx=8, pady=6)

        ctk.CTkLabel(self._cat_grid, text="文件类型", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                    text_color=COLOR_DIM).grid(row=0, column=0, padx=(0, 8), sticky="nw")

        top_level_cats = [(cid, cinfo) for cid, cinfo in CATEGORY_TREE.items() if cinfo.get("parent") is None]

        self._cat_child_containers = {}
        self._cat_color_btns = {}
        self._cat_tag_frames = {}
        self._child_checkboxes = {}
        self._parent_checkboxes = {}
        self._cat_expanded = False
        self._cat_col_map = {}
        self._cat_cell_frames = {}
        self._cat_dropdowns = {}

        col_idx = 1
        for cat_id, cat_info in top_level_cats:
            default_val = saved_enabled.get(cat_id, True)
            var = ctk.BooleanVar(value=default_val)
            self.preset_vars[cat_id] = var

            has_children = "children" in cat_info
            cmd = (lambda cid=cat_id: self.on_parent_toggle(cid)) if has_children else self.on_category_toggle

            cell_frame = ctk.CTkFrame(self._cat_grid, fg_color="#1e1e1e")
            cell_frame.grid(row=0, column=col_idx, padx=7, pady=2, sticky="nw")

            primary_row = ctk.CTkFrame(cell_frame, fg_color="#1e1e1e")
            primary_row.pack(fill="x")

            _, parent_cb, _ = self._create_cat_tag_row(primary_row, cat_id, cat_info, var, cmd)
            self._parent_checkboxes[cat_id] = parent_cb

            self._cat_col_map[cat_id] = col_idx
            self._cat_cell_frames[cat_id] = cell_frame
            col_idx += 1

        expand_col = col_idx
        self._expand_all_btn = ctk.CTkButton(self._cat_grid, text="📂 全部展开", width=80, height=26,
                                             fg_color="#333", hover_color=COLOR_RED, text_color=COLOR_TEXT,
                                             font=ctk.CTkFont(family=FONT_FAMILY, size=11), command=self._toggle_all_categories)
        self._expand_all_btn.grid(row=0, column=expand_col, padx=(6, 4), sticky="nw")

        self.merged_frame = ctk.CTkFrame(self.main_frame, fg_color="#1e1e1e", border_color=COLOR_BORDER, border_width=1)
        self.merged_frame.pack(fill="x", padx=10, pady=2)

        merged_row = ctk.CTkFrame(self.merged_frame, fg_color="#1e1e1e")
        merged_row.pack(fill="x", padx=8, pady=6)

        ctk.CTkLabel(merged_row, text="过滤条件", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                    text_color=COLOR_DIM).pack(side="left", padx=(0, 6))
        ctk.CTkLabel(merged_row, text="时间 ≥", font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_TEXT).pack(side="left", padx=(0, 2))

        self.days_var = ctk.CTkComboBox(merged_row, values=["0", "7", "30", "90", "180", "365"],
                                       width=65, height=26, fg_color="#2a2a2a", border_color="#444",
                                       text_color=COLOR_TEXT, dropdown_fg_color="#2a2a2a",
                                       dropdown_hover_color=COLOR_RED_LIGHT, dropdown_text_color=COLOR_TEXT,
                                       button_color=COLOR_RED, button_hover_color=COLOR_RED_LIGHT,
                                       font=ctk.CTkFont(family=FONT_FAMILY, size=12), command=lambda v: self._auto_save())
        self.days_var.set(self.settings.get("days_value", "0"))
        self.days_var.pack(side="left", padx=(0, 2))

        ctk.CTkLabel(merged_row, text="天前", font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_TEXT).pack(side="left", padx=(0, 8))

        self.size_enabled_var = ctk.BooleanVar(value=self.settings.get("size_enabled", False))
        ctk.CTkCheckBox(merged_row, text="大小", variable=self.size_enabled_var,
                       command=self.toggle_file_size_condition, fg_color=COLOR_RED, hover_color=COLOR_RED_LIGHT,
                       checkmark_color=COLOR_TEXT, text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=12)).pack(side="left", padx=(0, 2))

        self.size_operator_var = ctk.StringVar(value=self.settings.get("size_operator", ">"))
        ctk.CTkOptionMenu(merged_row, variable=self.size_operator_var, values=[">", "<"],
                        command=lambda v: self.update_file_size_condition(), width=45, height=26,
                        fg_color="#2a2a2a", button_color=COLOR_RED, button_hover_color=COLOR_RED_LIGHT,
                        text_color=COLOR_TEXT, dropdown_fg_color="#2a2a2a",
                        dropdown_hover_color=COLOR_RED_LIGHT, dropdown_text_color=COLOR_TEXT,
                        font=ctk.CTkFont(family=FONT_FAMILY, size=12)).pack(side="left", padx=(0, 2))

        self.size_value_entry = ctk.CTkEntry(merged_row, placeholder_text="值", width=55, height=26,
                                           fg_color="#2a2a2a", border_color="#444", text_color=COLOR_TEXT,
                                           placeholder_text_color=COLOR_DIM, font=ctk.CTkFont(family=FONT_FAMILY, size=12))
        sv = self.settings.get("size_value", "")
        if sv:
            self.size_value_entry.insert(0, sv)
        self.size_value_entry.pack(side="left", padx=(0, 2))

        self.size_unit_var = ctk.StringVar(value=self.settings.get("size_unit", "MB"))
        ctk.CTkOptionMenu(merged_row, variable=self.size_unit_var, values=["KB", "MB", "GB"],
                        command=lambda v: self.update_file_size_condition(), width=50, height=26,
                        fg_color="#2a2a2a", button_color=COLOR_RED, button_hover_color=COLOR_RED_LIGHT,
                        text_color=COLOR_TEXT, dropdown_fg_color="#2a2a2a",
                        dropdown_hover_color=COLOR_RED_LIGHT, dropdown_text_color=COLOR_TEXT,
                        font=ctk.CTkFont(family=FONT_FAMILY, size=12)).pack(side="left", padx=(0, 8))

        self.mode_var = ctk.StringVar(value=self.settings.get("mode_value", "stacked"))
        ctk.CTkOptionMenu(merged_row, variable=self.mode_var, values=["stacked", "filtered"],
                        command=lambda v: self._auto_save(), width=70, height=26,
                        fg_color="#2a2a2a", button_color=COLOR_RED, button_hover_color=COLOR_RED_LIGHT,
                        text_color=COLOR_TEXT, dropdown_fg_color="#2a2a2a",
                        dropdown_hover_color=COLOR_RED_LIGHT, dropdown_text_color=COLOR_TEXT,
                        font=ctk.CTkFont(family=FONT_FAMILY, size=12)).pack(side="left", padx=(0, 2))
        ctk.CTkLabel(merged_row, text="叠加|筛选", font=ctk.CTkFont(family=FONT_FAMILY, size=10), text_color=COLOR_DIM).pack(side="left", padx=(0, 12))

        sep = ctk.CTkFrame(merged_row, fg_color="#444", width=1, height=20)
        sep.pack(side="left", padx=(0, 8))

        self.custom_enabled_var = ctk.BooleanVar(value=self.settings.get("custom_enabled", False))
        self._make_color_tag(merged_row, "自定义规则", "custom", self.custom_enabled_var,
                            self.on_category_toggle, font_size=12)

        self.custom_rule_type_var = ctk.StringVar(value="suffix")
        ctk.CTkOptionMenu(merged_row, variable=self.custom_rule_type_var,
                        values=["suffix", "regex", "name_fuzzy", "name_exact"],
                        width=90, height=26, fg_color="#2a2a2a", button_color=COLOR_RED,
                        button_hover_color=COLOR_RED_LIGHT, text_color=COLOR_TEXT,
                        dropdown_fg_color="#2a2a2a", dropdown_hover_color=COLOR_RED_LIGHT,
                        dropdown_text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=11)).pack(side="left", padx=(4, 4))

        self.custom_rule_entry = ctk.CTkEntry(merged_row, placeholder_text="后缀/正则/文件名...",
                                             fg_color="#2a2a2a", border_color="#444", text_color=COLOR_TEXT,
                                             placeholder_text_color=COLOR_DIM, height=26, font=ctk.CTkFont(family=FONT_FAMILY, size=12))
        self.custom_rule_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))

        ctk.CTkButton(merged_row, text="+", width=26, height=26, command=self.add_custom_rule,
                     fg_color=COLOR_RED, hover_color=COLOR_RED_LIGHT, text_color=COLOR_TEXT,
                     font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold")).pack(side="left", padx=(0, 2))
        ctk.CTkButton(merged_row, text="✕", width=26, height=26, command=self.clear_custom_rules,
                     fg_color="#333", hover_color=COLOR_RED, text_color=COLOR_TEXT,
                     font=ctk.CTkFont(family=FONT_FAMILY, size=11)).pack(side="left")

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
        if self._cat_expanded:
            for cat_id, dropdown in list(self._cat_dropdowns.items()):
                dropdown.destroy()
            self._cat_dropdowns.clear()
            self._cat_expanded = False
            self._expand_all_btn.configure(text="📂 全部展开")
            return
        self._cat_expanded = True
        self._expand_all_btn.configure(text="📂 全部折叠")

        for cat_id, cell_frame in self._cat_cell_frames.items():
            cat_info = CATEGORY_TREE.get(cat_id, {})
            children = cat_info.get("children", [])
            if not children:
                continue

            parent_bg = self.category_colors.get(cat_id, COLOR_BG)

            dropdown = ctk.CTkFrame(cell_frame, fg_color="#1e1e1e", corner_radius=0)
            dropdown.pack(fill="x", pady=(2, 0))

            for child_id in children:
                child_info_d = CATEGORY_TREE.get(child_id, {})
                if child_id not in self.preset_vars:
                    default_val_c = self.settings.get("enabled_categories", {}).get(child_id, True)
                    child_var = ctk.BooleanVar(value=default_val_c)
                    self.preset_vars[child_id] = child_var

                child_row = ctk.CTkFrame(dropdown, fg_color="#1e1e1e")
                child_row.pack(fill="x", pady=1)

                _, child_cb, _ = self._create_cat_tag_row(
                    child_row, child_id, child_info_d, self.preset_vars[child_id],
                    lambda cid=child_id: self.on_child_toggle(cid),
                    font_size=11, height=22, parent_color=parent_bg)
                self._child_checkboxes[child_id] = child_cb

            self._cat_dropdowns[cat_id] = dropdown

    def _pick_color_inline(self, cat_id):
        cat_info = CATEGORY_TREE.get(cat_id, {})
        is_child = "parent" in cat_info
        if is_child:
            current = CATEGORY_TEXT_COLORS.get(cat_id, COLOR_TEXT)
            result = colorchooser.askcolor(color=current, title="选择文字颜色")
            if result and result[1]:
                CATEGORY_TEXT_COLORS[cat_id] = result[1]
                self._update_tag_styles()
                self._auto_save()
        else:
            current = self.category_colors.get(cat_id, COLOR_BG)
            result = colorchooser.askcolor(color=current, title="选择背景颜色")
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
            parent_cb = self._parent_checkboxes.get(cat_id)
            if parent_cb:
                parent_cb.configure(bg_color=color)
        for child_id, child_cb in self._child_checkboxes.items():
            child_info = CATEGORY_TREE.get(child_id, {})
            parent_id = child_info.get("parent")
            parent_bg = self.category_colors.get(parent_id, COLOR_BG) if parent_id else COLOR_BG
            text_color = CATEGORY_TEXT_COLORS.get(child_id, COLOR_TEXT)
            child_cb.configure(text_color=text_color, checkmark_color=text_color, bg_color=parent_bg)
            child_tag_frame = self._cat_tag_frames.get(child_id)
            if child_tag_frame:
                child_tag_frame.configure(fg_color=parent_bg)
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

        batch_check = []
        batch_uncheck = []
        for item in self.tree.get_children():
            values = self.tree.item(item, "values")
            tags = self.tree.item(item, "tags")
            file_path = tags[0] if tags else ""
            category = values[6] if len(values) > 6 else ""
            cat_key = CATEGORY_TO_CHECKBOX.get(category, "")
            if cat_key and cat_key in active:
                self.selected_files.add(file_path)
                batch_check.append(item)
            else:
                self.selected_files.discard(file_path)
                batch_uncheck.append(item)
        for item in batch_check:
            vals = list(self.tree.item(item, "values"))
            vals[0] = "☑"
            self.tree.item(item, values=vals)
        for item in batch_uncheck:
            vals = list(self.tree.item(item, "values"))
            vals[0] = "☐"
            self.tree.item(item, values=vals)
        self._recompute_selected_size()
        self._update_selected_size_display()

    def _destroy_current_panel(self):
        if self._current_panel is not None:
            self._current_panel.destroy()
            self._current_panel = None
            self._current_panel_type = None
        if self._cat_expanded:
            for cat_id, dropdown in list(self._cat_dropdowns.items()):
                dropdown.destroy()
            self._cat_dropdowns.clear()
            self._cat_expanded = False
            if hasattr(self, '_expand_all_btn'):
                self._expand_all_btn.configure(text="📂 全部展开")

    def toggle_settings_panel(self):
        if self._current_panel_type == "settings":
            self._destroy_current_panel()
            return
        self._destroy_current_panel()
        panel = ctk.CTkFrame(self.main_frame, fg_color="#252525", border_color="#444", border_width=1)
        panel.pack(fill="x", padx=10, pady=(2, 2), after=self._func_frame)
        self._current_panel = panel
        self._current_panel_type = "settings"
        sys_info = self.settings.get("sys_info", get_system_info())
        rec = self.settings.get("recommended", recommend_params(sys_info))
        hw_row = ctk.CTkFrame(panel, fg_color="#252525")
        hw_row.pack(fill="x", padx=10, pady=(8, 4))
        ctk.CTkLabel(hw_row, text=f"💻 {sys_info['total_ram_gb']}GB | {sys_info['cpu_physical']}核{sys_info['cpu_logical']}线程",
                    font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_DIM).pack(side="left")
        params_row = ctk.CTkFrame(panel, fg_color="#252525")
        params_row.pack(fill="x", padx=10, pady=4)
        entries = {}
        items = [
            ("max_display", "显示上限", str(self._max_display), str(rec["max_display"])),
            ("max_depth", "递归深度", str(self._max_depth), str(rec["max_depth"])),
            ("batch_size", "批量大小", str(self._batch_size), str(rec["batch_size"])),
            ("flush_interval", "刷新间隔", str(self._flush_interval), str(rec["flush_interval"])),
        ]
        for key, label, current, default in items:
            ctk.CTkLabel(params_row, text=label, font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_TEXT).pack(side="left", padx=(0, 2))
            entry = ctk.CTkEntry(params_row, width=60, height=26, fg_color="#2a2a2a", border_color="#444",
                               text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=12))
            entry.pack(side="left", padx=(0, 2))
            entry.insert(0, current)
            entries[key] = entry
        btn_row = ctk.CTkFrame(panel, fg_color="#252525")
        btn_row.pack(fill="x", padx=10, pady=(4, 8))

        def apply_rec():
            for key, _, _, default in items:
                entries[key].delete(0, "end")
                entries[key].insert(0, default)
            save_inline()

        def save_inline():
            try:
                self._max_display = int(entries["max_display"].get())
                self._max_depth = int(entries["max_depth"].get())
                self._batch_size = int(entries["batch_size"].get())
                self._flush_interval = float(entries["flush_interval"].get())
                self.settings.update({"max_display": self._max_display, "max_depth": self._max_depth,
                                     "batch_size": self._batch_size, "flush_interval": self._flush_interval})
                save_settings(self.settings)
            except ValueError:
                pass

        for key in entries:
            entries[key].bind("<Return>", lambda e: save_inline())
            entries[key].bind("<FocusOut>", lambda e: save_inline())

        ctk.CTkButton(btn_row, text="应用推荐值", height=26, fg_color="#333", hover_color=COLOR_RED,
                     text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=12), command=apply_rec).pack(side="left", padx=(0, 5))

    def toggle_delete_settings_panel(self):
        if self._current_panel_type == "delete":
            self._destroy_current_panel()
            return
        self._destroy_current_panel()
        panel = ctk.CTkFrame(self.main_frame, fg_color="#252525", border_color="#444", border_width=1)
        panel.pack(fill="x", padx=10, pady=(2, 2), after=self._func_frame)
        self._current_panel = panel
        self._current_panel_type = "delete"
        mode_row = ctk.CTkFrame(panel, fg_color="#252525")
        mode_row.pack(fill="x", padx=10, pady=(8, 4))
        ctk.CTkLabel(mode_row, text="删除方式", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"), text_color=COLOR_TEXT).pack(side="left", padx=(0, 10))
        del_mode_var = ctk.StringVar(value=self.delete_mode)
        for val, label in [("permanent", "彻底删除"), ("recycle", "删除到回收站"), ("move", "移动到文件夹"), ("compress", "压缩为压缩包")]:
            ctk.CTkRadioButton(mode_row, text=label, variable=del_mode_var, value=val,
                              fg_color=COLOR_RED, hover_color=COLOR_RED_LIGHT, text_color=COLOR_TEXT,
                              font=ctk.CTkFont(family=FONT_FAMILY, size=12)).pack(side="left", padx=5)
        detail_row = ctk.CTkFrame(panel, fg_color="#252525")
        detail_row.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(detail_row, text="移动目录", font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_TEXT).pack(side="left", padx=(0, 4))
        move_dir_entry = ctk.CTkEntry(detail_row, placeholder_text="选择移动目标文件夹...",
                                     fg_color="#2a2a2a", border_color="#444", text_color=COLOR_TEXT,
                                     placeholder_text_color=COLOR_DIM, height=26, font=ctk.CTkFont(family=FONT_FAMILY, size=12), width=300)
        move_dir_entry.pack(side="left", padx=(0, 4))
        move_dir_entry.insert(0, self.delete_move_dir)

        def browse_move():
            d = filedialog.askdirectory(title="选择移动目标文件夹")
            if d:
                move_dir_entry.delete(0, "end")
                move_dir_entry.insert(0, d)

        ctk.CTkButton(detail_row, text="浏览", width=50, height=26, command=browse_move,
                     fg_color="#333", hover_color=COLOR_RED, text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=12)).pack(side="left", padx=(0, 12))
        ctk.CTkLabel(detail_row, text="压缩包名", font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_TEXT).pack(side="left", padx=(0, 4))
        zip_name_entry = ctk.CTkEntry(detail_row, placeholder_text="如 cleanup_{date}",
                                     fg_color="#2a2a2a", border_color="#444", text_color=COLOR_TEXT,
                                     placeholder_text_color=COLOR_DIM, height=26, font=ctk.CTkFont(family=FONT_FAMILY, size=12), width=180)
        zip_name_entry.pack(side="left", padx=(0, 4))
        zip_name_entry.insert(0, self.delete_zip_name)
        ctk.CTkLabel(detail_row, text="{date}=日期 {time}=时间", font=ctk.CTkFont(family=FONT_FAMILY, size=10), text_color=COLOR_DIM).pack(side="left")
        btn_row = ctk.CTkFrame(panel, fg_color="#252525")
        btn_row.pack(fill="x", padx=10, pady=(4, 8))

        def save_del():
            self.delete_mode = del_mode_var.get()
            self.delete_move_dir = move_dir_entry.get().strip()
            self.delete_zip_name = zip_name_entry.get().strip() or "cleanup_{date}"
            self.settings.update({"delete_mode": self.delete_mode, "delete_move_dir": self.delete_move_dir,
                                 "delete_zip_name": self.delete_zip_name})
            save_settings(self.settings)

        del_mode_var.trace_add("write", lambda *a: save_del())
        move_dir_entry.bind("<FocusOut>", lambda e: save_del())
        zip_name_entry.bind("<FocusOut>", lambda e: save_del())
        move_dir_entry.bind("<Return>", lambda e: save_del())
        zip_name_entry.bind("<Return>", lambda e: save_del())

    def toggle_preset_rules_panel(self):
        if self._current_panel_type == "preset":
            self._destroy_current_panel()
            return
        self._destroy_current_panel()
        panel = ctk.CTkFrame(self.main_frame, fg_color="#252525", border_color="#444", border_width=1)
        panel.pack(fill="x", padx=10, pady=(2, 2), after=self._func_frame)
        self._current_panel = panel
        self._current_panel_type = "preset"

        rules_container = ctk.CTkFrame(panel, fg_color="#252525")
        rules_container.pack(fill="x", padx=10, pady=(6, 4))
        rules_container.grid_columnconfigure(0, weight=1)
        rules_container.grid_columnconfigure(1, weight=1)

        rule_check_vars = {}
        col = 0
        row_idx = 0
        for rule_id, rule_info in PRESET_RULE_PACKS.items():
            cell = ctk.CTkFrame(rules_container, fg_color="#252525")
            cell.grid(row=row_idx, column=col, padx=2, pady=1, sticky="w")

            is_active = rule_id in self._active_rule_packs
            var = ctk.BooleanVar(value=is_active)
            rule_check_vars[rule_id] = var

            ctk.CTkCheckBox(cell, text=rule_info["name"], variable=var, fg_color=COLOR_RED,
                          hover_color=COLOR_RED_LIGHT, checkmark_color=COLOR_TEXT,
                          text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                          command=lambda rid=rule_id: self._on_rule_pack_toggle(rid)).pack(side="left", padx=(0, 4))

            ctk.CTkLabel(cell, text=rule_info["desc"], font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                        text_color=COLOR_DIM).pack(side="left")

            col += 1
            if col >= 2:
                col = 0
                row_idx += 1

        btn_row = ctk.CTkFrame(panel, fg_color="#252525")
        btn_row.pack(fill="x", padx=10, pady=(4, 8))

        def save_rules():
            self._active_rule_packs = {rid for rid, v in rule_check_vars.items() if v.get()}
            self.settings["active_rule_packs"] = list(self._active_rule_packs)
            self._apply_rule_packs()
            save_settings(self.settings)

        for rid, v in rule_check_vars.items():
            v.trace_add("write", lambda *a, rid=rid: save_rules())

        ctk.CTkButton(btn_row, text="全选", height=26, fg_color="#333", hover_color=COLOR_RED,
                     text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                     command=lambda: [v.set(True) for v in rule_check_vars.values()]).pack(side="left", padx=(0, 5))
        ctk.CTkButton(btn_row, text="全不选", height=26, fg_color="#333", hover_color=COLOR_RED,
                     text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                     command=lambda: [v.set(False) for v in rule_check_vars.values()]).pack(side="left", padx=(0, 5))
        ctk.CTkButton(btn_row, text="📁 导入规则", height=26, fg_color="#333", hover_color=COLOR_RED,
                     text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=12), command=self._import_custom_rule_pack).pack(side="left", padx=5)
        ctk.CTkButton(btn_row, text="📤 导出规则", height=26, fg_color="#333", hover_color=COLOR_RED,
                     text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=12), command=self._export_custom_rule_pack).pack(side="left", padx=5)

    def _on_rule_pack_toggle(self, rule_id):
        pass

    def _apply_rule_packs(self):
        active_categories = set()
        for rule_id in self._active_rule_packs:
            rule = PRESET_RULE_PACKS.get(rule_id, {})
            for cat in rule.get("categories", []):
                active_categories.add(cat)
        for cat_id, var in self.preset_vars.items():
            var.set(cat_id in active_categories or cat_id == "custom")
        self.on_category_toggle()

    def _import_custom_rule_pack(self):
        fpath = filedialog.askopenfilename(title="选择规则包文件", filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")])
        if not fpath:
            return
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, dict) or "name" not in data or "categories" not in data:
                messagebox.showerror("导入失败", "无效的规则包格式，需包含name和categories字段")
                return
            rule_id = f"custom_{int(time.time())}"
            PRESET_RULE_PACKS[rule_id] = data
            self._active_rule_packs.add(rule_id)
            self.settings["active_rule_packs"] = list(self._active_rule_packs)
            custom_packs = self.settings.get("custom_rule_packs", {})
            custom_packs[rule_id] = data
            self.settings["custom_rule_packs"] = custom_packs
            save_settings(self.settings)
            self._destroy_current_panel()
            messagebox.showinfo("导入成功", f"规则包 '{data['name']}' 已导入")
        except Exception as e:
            messagebox.showerror("导入失败", f"读取文件出错: {e}")

    def _export_custom_rule_pack(self):
        fpath = filedialog.asksaveasfilename(title="导出规则包", defaultextension=".json",
                                            filetypes=[("JSON文件", "*.json")])
        if not fpath:
            return
        export_data = {}
        for rule_id in self._active_rule_packs:
            rule = PRESET_RULE_PACKS.get(rule_id, {})
            if rule:
                export_data[rule_id] = rule
        if not export_data:
            messagebox.showwarning("导出失败", "没有已激活的规则包可导出")
            return
        try:
            merged = {"name": "自定义规则包", "desc": "导出的规则包合集",
                     "categories": list(set(c for rid, r in export_data.items() for c in r.get("categories", []))),
                     "extensions": {k: v for rid, r in export_data.items() for k, v in r.get("extensions", {}).items()}}
            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump(merged, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("导出成功", f"规则包已导出到: {fpath}")
        except Exception as e:
            messagebox.showerror("导出失败", f"写入文件出错: {e}")

    def toggle_analysis_report(self):
        if self._current_panel_type == "analysis":
            self._destroy_current_panel()
            return
        self._destroy_current_panel()
        panel = ctk.CTkFrame(self.main_frame, fg_color="#252525", border_color="#444", border_width=1)
        panel.pack(fill="x", padx=10, pady=(2, 2), after=self._func_frame)
        self._current_panel = panel
        self._current_panel_type = "analysis"

        content_row = ctk.CTkFrame(panel, fg_color="#252525")
        content_row.pack(fill="x", padx=12, pady=(6, 8))
        content_row.grid_columnconfigure(0, weight=0)
        content_row.grid_columnconfigure(1, weight=0)
        content_row.grid_columnconfigure(2, weight=1)

        chart_col = ctk.CTkFrame(content_row, fg_color="#252525")
        chart_col.grid(row=0, column=0, padx=(0, 6), pady=0, sticky="n")
        ctk.CTkLabel(chart_col, text="分类占比", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
                     text_color=COLOR_TEXT).pack(anchor="w", padx=4, pady=(0, 2))
        self._report_chart = tk.Canvas(chart_col, bg="#252525", highlightthickness=0, width=220, height=200)
        self._report_chart.pack(padx=0, pady=0)

        legend_col = ctk.CTkFrame(content_row, fg_color="#252525", corner_radius=0)
        legend_col.grid(row=0, column=1, padx=(0, 12), pady=0, sticky="ns")
        ctk.CTkLabel(legend_col, text="占比分析", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
                     text_color=COLOR_TEXT).pack(anchor="w", padx=4, pady=(0, 2))
        self._report_legend_frame = ctk.CTkFrame(legend_col, fg_color="#252525", corner_radius=0, width=240)
        self._report_legend_frame.pack(fill="both", expand=True, padx=0, pady=0)

        stats_advice_col = ctk.CTkFrame(content_row, fg_color="#2a2a2a", corner_radius=8, border_width=1, border_color="#444")
        stats_advice_col.grid(row=0, column=2, sticky="nsew", padx=0, pady=0)

        stats_header = ctk.CTkFrame(stats_advice_col, fg_color="#2a2a2a")
        stats_header.pack(fill="x", padx=10, pady=(8, 2))
        ctk.CTkLabel(stats_header, text="📋 扫描统计", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                     text_color=COLOR_TEXT).pack(side="left")

        self._report_stats_label = ctk.CTkLabel(stats_advice_col, text="", font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                                                 text_color=COLOR_TEXT, justify="left", anchor="w")
        self._report_stats_label.pack(fill="x", padx=14, pady=(0, 4))

        sep = ctk.CTkFrame(stats_advice_col, fg_color="#444", height=1)
        sep.pack(fill="x", padx=8, pady=2)

        advice_header = ctk.CTkFrame(stats_advice_col, fg_color="#2a2a2a")
        advice_header.pack(fill="x", padx=10, pady=(4, 2))
        ctk.CTkLabel(advice_header, text="💡 建议处理方案", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                     text_color=COLOR_TEXT).pack(side="left")

        self._report_advice_label = ctk.CTkLabel(stats_advice_col, text="", font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                                                  text_color=COLOR_TEXT, justify="left", anchor="w", wraplength=800)
        self._report_advice_label.pack(fill="x", padx=14, pady=(0, 8))

        self._report_stats_label.configure(text="正在校验文件...")
        self._report_advice_label.configure(text="请稍候...")
        threading.Thread(target=self._do_verify_and_build_report_bg, daemon=True).start()

    def toggle_version_panel(self):
        if self._current_panel_type == "version":
            self._close_version_page()
            return
        self._destroy_current_panel()
        self._show_version_page()

    def _show_version_page(self):
        self._current_panel_type = "version"
        for w in self.main_frame.winfo_children():
            if w != self.status_frame:
                w.destroy()

        page = ctk.CTkFrame(self.main_frame, fg_color=COLOR_BG)
        page.pack(fill="both", expand=True, padx=0, pady=0, before=self.status_frame)
        self._current_panel = page

        top_bar = ctk.CTkFrame(page, fg_color="#1e1e1e", corner_radius=0)
        top_bar.pack(fill="x", padx=0, pady=0)
        ctk.CTkButton(top_bar, text="← 返回扫描", width=90, height=30, fg_color="#333", hover_color=COLOR_RED,
                     text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                     command=self._close_version_page).pack(side="left", padx=10, pady=8)
        ctk.CTkLabel(top_bar, text="🔄 软件更新与版本管理", font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
                    text_color=COLOR_TEXT).pack(side="left", padx=5)
        ctk.CTkLabel(top_bar, text=f"v{VERSION}", font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                    text_color=COLOR_DIM).pack(side="left", padx=10)
        self._ver_status_label = ctk.CTkLabel(top_bar, text="", font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                                              text_color=COLOR_DIM)
        self._ver_status_label.pack(side="right", padx=10)
        ctk.CTkButton(top_bar, text="🔄 检查远程更新", height=28, fg_color="#333", hover_color=COLOR_RED,
                     text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                     command=self._check_remote_versions).pack(side="right", padx=5, pady=6)

        scroll = ctk.CTkScrollableFrame(page, fg_color=COLOR_BG, corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        self._ver_info_frame = ctk.CTkFrame(scroll, fg_color="#1e1e1e", corner_radius=6)
        self._ver_info_frame.pack(fill="x", padx=10, pady=(6, 2))
        self._ver_info_label = ctk.CTkLabel(self._ver_info_frame, text="点击「检查远程更新」查看最新版本",
                                            font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_DIM,
                                            wraplength=600, justify="left")
        self._ver_info_label.pack(padx=12, pady=8, anchor="w")

        sep1 = ctk.CTkFrame(scroll, fg_color="#333", height=1)
        sep1.pack(fill="x", padx=10, pady=(4, 2))

        ctk.CTkLabel(scroll, text="📦 稳定版本", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                    text_color=COLOR_RED).pack(anchor="w", padx=14, pady=(6, 2))

        self._ver_stable_container = ctk.CTkFrame(scroll, fg_color=COLOR_BG)
        self._ver_stable_container.pack(fill="x", padx=10, pady=2)

        sep2 = ctk.CTkFrame(scroll, fg_color="#333", height=1)
        sep2.pack(fill="x", padx=10, pady=(8, 2))

        git_header = ctk.CTkFrame(scroll, fg_color=COLOR_BG)
        git_header.pack(fill="x", padx=10, pady=(4, 2))
        ctk.CTkLabel(git_header, text="🔀 Git 版本切换", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
                    text_color="#42A5F5").pack(side="left", padx=4)
        ctk.CTkButton(git_header, text="刷新历史", width=70, height=24, fg_color="#2a2a2a", hover_color="#3a3a3a",
                     text_color="#aaa", font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                     command=self._refresh_git_history).pack(side="right", padx=4)

        self._ver_git_container = ctk.CTkFrame(scroll, fg_color=COLOR_BG)
        self._ver_git_container.pack(fill="x", padx=10, pady=2)

        self._ver_status_label.configure(text="加载中...")
        self.root.after(100, self._load_all_versions)

    def _close_version_page(self):
        self._current_panel_type = None
        for w in self.main_frame.winfo_children():
            w.destroy()
        self._current_panel = None
        self._ver_info_frame = None
        self._ver_info_label = None
        self._ver_stable_container = None
        self._ver_git_container = None
        self._ver_status_label = None
        self._restore_main_ui()

    def _restore_main_ui(self):
        self.setup_status_bar()
        self.setup_scan_conditions()
        self.setup_control_panel()
        self.setup_table_area()
        if self.file_list:
            self.update_scan_conditions()
            self.display_files()

    def _get_project_root(self):
        if getattr(sys, 'frozen', False):
            return os.path.dirname(os.path.dirname(sys.executable))
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def _get_dev_dir(self):
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _run_git(self, *args, cwd=None, timeout=60):
        import subprocess
        cmd = ["git"] + list(args)
        try:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            r = subprocess.run(cmd, cwd=cwd or self._get_project_root(),
                              capture_output=True, text=True, timeout=timeout,
                              startupinfo=si,
                              creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            return {"ok": r.returncode == 0, "stdout": r.stdout.strip(), "stderr": r.stderr.strip()}
        except subprocess.TimeoutExpired:
            return {"ok": False, "stdout": "", "stderr": "命令超时"}
        except Exception as e:
            return {"ok": False, "stdout": "", "stderr": str(e)}

    def _is_git_repo(self):
        r = self._run_git("rev-parse", "--is-inside-work-tree")
        return r["ok"] and r["stdout"] == "true"

    def _get_current_commit(self):
        r = self._run_git("rev-parse", "--short", "HEAD")
        return r["stdout"] if r["ok"] else "unknown"

    def _list_stable_exes(self):
        dev_dir = self._get_dev_dir()
        ver_dir = os.path.join(dev_dir, "ver")
        if not os.path.isdir(ver_dir):
            return []
        import re
        exes = []
        for f in os.listdir(ver_dir):
            if f.endswith(".exe") and "云集智能文件清理专家" in f:
                path = os.path.join(ver_dir, f)
                m = re.search(r'v(\d+\.\d+\.\d+\.\d+)', f)
                ver = m.group(1) if m else "unknown"
                size_mb = round(os.path.getsize(path) / (1024 * 1024), 1)
                exes.append({"filename": f, "path": path, "version": ver, "size_mb": size_mb})
        exes.sort(key=lambda x: x["version"], reverse=True)
        return exes

    def _get_local_version_history(self):
        dev_dir = self._get_dev_dir()
        path = os.path.join(dev_dir, "app", "version_history.json")
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            return []
        except Exception:
            return []

    def _get_git_history(self, limit=30):
        if not self._is_git_repo():
            return []
        r = self._run_git("log", f"-{limit}", "--oneline", "--format=%h|%s|%an|%ar", timeout=30)
        if not r["ok"]:
            return []
        commits = []
        for line in r["stdout"].splitlines():
            parts = line.strip().split("|", 3)
            if len(parts) >= 4:
                commits.append({"hash": parts[0], "message": parts[1], "author": parts[2], "time": parts[3]})
        return commits

    def _load_all_versions(self):
        if self._ver_status_label is not None and self._ver_status_label.winfo_exists():
            self._ver_status_label.configure(text="正在加载版本信息...")
        threading.Thread(target=self._do_load_all_versions, daemon=True).start()

    def _do_load_all_versions(self):
        stable_exes = self._list_stable_exes()
        exe_versions = {e["version"]: e for e in stable_exes}
        local_versions = self._get_local_version_history()
        git_commits = self._get_git_history(30)

        current_version = VERSION

        local_ver_set = set()
        all_versions = []
        import re
        for v in local_versions:
            ver = v.get("version", "")
            m = re.search(r'v?(\d+\.\d+\.\d+\.\d+)', ver)
            ver_num = m.group(1) if m else ver
            if not ver_num:
                continue
            local_ver_set.add(ver_num)
            all_versions.append({
                "version": ver_num,
                "name": v.get("name", f"v{ver_num}"),
                "changes": v.get("changes", []),
                "build_time": v.get("build_time", v.get("date", "")),
                "git_commit": v.get("git_commit", ""),
                "available": ver_num in exe_versions,
                "exe_info": exe_versions.get(ver_num),
                "is_remote_new": False,
            })

        for ver, exe in exe_versions.items():
            if ver not in local_ver_set:
                all_versions.append({
                    "version": ver,
                    "name": exe["filename"],
                    "changes": [],
                    "build_time": "",
                    "git_commit": "",
                    "available": True,
                    "exe_info": exe,
                    "is_remote_new": False,
                })

        all_versions.sort(key=lambda x: x["version"], reverse=True)

        def update_ui():
            if self._ver_stable_container is not None and self._ver_stable_container.winfo_exists():
                self._render_stable_versions(all_versions, current_version)
            if self._ver_git_container is not None and self._ver_git_container.winfo_exists():
                self._render_git_history(git_commits)
            if self._ver_status_label is not None and self._ver_status_label.winfo_exists():
                self._ver_status_label.configure(text=f"稳定版 {len(all_versions)} 个 | Git提交 {len(git_commits)} 条")

        self.root.after(0, update_ui)

    def _render_stable_versions(self, all_versions, current_version):
        for w in self._ver_stable_container.winfo_children():
            w.destroy()

        if not all_versions:
            ctk.CTkLabel(self._ver_stable_container, text="暂无稳定版本",
                        font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=COLOR_DIM).pack(padx=12, pady=10)
            return

        for v in all_versions:
            ver = v["version"]
            is_current = (ver == current_version)
            is_available = v.get("available", False)
            is_remote_new = v.get("is_remote_new", False)
            changes = v.get("changes", [])
            exe_info = v.get("exe_info")

            if is_current:
                card_bg = "#162016"
                border_color = "#1f3a1f"
            elif is_remote_new:
                card_bg = "#161620"
                border_color = "#1f3a4f"
            elif is_available:
                card_bg = "#161616"
                border_color = "#222"
            else:
                card_bg = "#111"
                border_color = "#1a1a1a"

            card = ctk.CTkFrame(self._ver_stable_container, fg_color=card_bg, corner_radius=6,
                               border_width=1, border_color=border_color)
            card.pack(fill="x", pady=3, padx=2)

            header = ctk.CTkFrame(card, fg_color=card_bg)
            header.pack(fill="x", padx=10, pady=(6, 2))

            ver_color = "#4CAF50" if is_current else ("#42A5F5" if is_remote_new else (COLOR_TEXT if is_available else COLOR_DIM))
            ctk.CTkLabel(header, text=f"v{ver}", font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
                        text_color=ver_color).pack(side="left")

            build_time = v.get("build_time", "")
            if build_time:
                ctk.CTkLabel(header, text=build_time[:16], font=ctk.CTkFont(family="Consolas", size=10),
                            text_color="#555").pack(side="left", padx=8)

            if is_remote_new:
                ctk.CTkLabel(header, text="🆕 远程新版本", font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                            text_color="#42A5F5").pack(side="left", padx=4)
            elif is_available and exe_info:
                ctk.CTkLabel(header, text="📦 含EXE稳定版", font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                            text_color="#FF9800").pack(side="left", padx=4)
                if exe_info.get("size_mb"):
                    ctk.CTkLabel(header, text=f"{exe_info['size_mb']}MB", font=ctk.CTkFont(family="Consolas", size=10),
                                text_color="#555").pack(side="left", padx=4)

            if is_current:
                ctk.CTkLabel(header, text="● 当前版本", font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                            text_color="#4CAF50").pack(side="right", padx=4)
            elif is_available and exe_info:
                ctk.CTkButton(header, text="切换", width=50, height=22, fg_color="#1e1e1e", hover_color="#2a2a2a",
                             text_color="#aaa", font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                             command=lambda p=exe_info["path"], gc=v.get("git_commit", ""): self._switch_to_exe(p, gc)).pack(side="right", padx=4)

            detail = ctk.CTkFrame(card, fg_color=card_bg)
            detail.pack(fill="x", padx=10, pady=(0, 6))

            git_commit = v.get("git_commit", "")
            if git_commit:
                ctk.CTkLabel(detail, text=f"🔗 commit: {git_commit}", font=ctk.CTkFont(family="Consolas", size=9),
                            text_color="#555").pack(anchor="w")

            if changes:
                for ch in changes[:3]:
                    ctk.CTkLabel(detail, text=f"· {ch}", font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                                text_color="#777", wraplength=500, justify="left").pack(anchor="w")
                if len(changes) > 3:
                    ctk.CTkLabel(detail, text=f"  +{len(changes)-3}项更多...", font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                                text_color="#444").pack(anchor="w")
            else:
                ctk.CTkLabel(detail, text="暂无修改记录", font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                            text_color="#3a3a3a").pack(anchor="w")

    def _render_git_history(self, git_commits):
        for w in self._ver_git_container.winfo_children():
            w.destroy()

        if not self._is_git_repo():
            ctk.CTkLabel(self._ver_git_container, text="当前不是 Git 仓库，无法使用 Git 版本切换",
                        font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color="#555").pack(pady=20)
            return

        if not git_commits:
            ctk.CTkLabel(self._ver_git_container, text="暂无 Git 提交记录",
                        font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color="#555").pack(pady=20)
            return

        current_commit = self._get_current_commit()

        for commit in git_commits:
            is_current = (commit["hash"] == current_commit)

            if is_current:
                card_bg = "#162016"
                border_color = "#1f3a1f"
            else:
                card_bg = "#161616"
                border_color = "#2a2a2a"

            card = ctk.CTkFrame(self._ver_git_container, fg_color=card_bg, corner_radius=6,
                               border_width=1, border_color=border_color)
            card.pack(fill="x", pady=2, padx=2)

            header = ctk.CTkFrame(card, fg_color=card_bg)
            header.pack(fill="x", padx=10, pady=(6, 2))

            hash_color = "#4CAF50" if is_current else "#42A5F5"
            ctk.CTkLabel(header, text=commit["hash"], font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                        text_color=hash_color).pack(side="left")

            ctk.CTkLabel(header, text=commit.get("time", ""), font=ctk.CTkFont(family="Consolas", size=9),
                        text_color="#666").pack(side="left", padx=8)

            if is_current:
                ctk.CTkLabel(header, text="● 当前", font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                            text_color="#4CAF50").pack(side="right", padx=4)
            else:
                ctk.CTkButton(header, text="切换", width=50, height=22, fg_color="#1e1e1e", hover_color="#2a2a2a",
                             text_color="#aaa", font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                             command=lambda h=commit["hash"]: self._switch_git_commit(h)).pack(side="right", padx=4)

            msg_frame = ctk.CTkFrame(card, fg_color=card_bg)
            msg_frame.pack(fill="x", padx=10, pady=(0, 6))
            ctk.CTkLabel(msg_frame, text=commit["message"], font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                        text_color="#ccc", wraplength=500, justify="left").pack(anchor="w")
            ctk.CTkLabel(msg_frame, text=f"👤 {commit.get('author', '')}", font=ctk.CTkFont(family=FONT_FAMILY, size=9),
                        text_color="#666").pack(anchor="w")

    def _refresh_git_history(self):
        if self._ver_git_container is None or not self._ver_git_container.winfo_exists():
            return
        git_commits = self._get_git_history(30)
        self._render_git_history(git_commits)

    def _check_remote_versions(self):
        if self._ver_status_label is not None and self._ver_status_label.winfo_exists():
            self._ver_status_label.configure(text="正在检查远程更新...")
        threading.Thread(target=self._do_check_remote, daemon=True).start()

    def _do_check_remote(self):
        try:
            import subprocess
            project_root = self._get_project_root()
            git_dir = os.path.join(project_root, ".git")
            if not os.path.isdir(git_dir):
                raise Exception("未找到Git仓库，无法检查远程更新")

            fetch_result = subprocess.run(["git", "fetch", "origin"], capture_output=True, text=True,
                                         cwd=project_root, timeout=30,
                                         creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            if fetch_result.returncode != 0:
                raise Exception(f"git fetch 失败: {fetch_result.stderr.strip()}")

            show_result = subprocess.run(["git", "show", "origin/main:dev/ver/version.json"],
                                        capture_output=True, text=True, cwd=project_root, timeout=10,
                                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            if show_result.returncode != 0:
                raise Exception(f"获取远程version.json失败: {show_result.stderr.strip()}")

            data = json.loads(show_result.stdout)
            remote_latest = data.get("latest", "")
            remote_versions = {v["version"]: v for v in data.get("versions", [])}

            stable_exes = self._list_stable_exes()
            exe_versions = {e["version"]: e for e in stable_exes}
            local_versions = self._get_local_version_history()
            git_commits = self._get_git_history(30)

            import re
            current_version = VERSION
            local_ver_set = set()
            all_versions = []

            for v in local_versions:
                ver = v.get("version", "")
                m = re.search(r'v?(\d+\.\d+\.\d+\.\d+)', ver)
                ver_num = m.group(1) if m else ver
                if not ver_num:
                    continue
                local_ver_set.add(ver_num)
                all_versions.append({
                    "version": ver_num,
                    "name": v.get("name", f"v{ver_num}"),
                    "changes": v.get("changes", []),
                    "build_time": v.get("build_time", v.get("date", "")),
                    "git_commit": v.get("git_commit", ""),
                    "available": ver_num in exe_versions,
                    "exe_info": exe_versions.get(ver_num),
                    "is_remote_new": False,
                })

            for rv, rinfo in remote_versions.items():
                m = re.search(r'v?(\d+\.\d+\.\d+\.\d+)', rv)
                ver_num = m.group(1) if m else rv
                if not ver_num or ver_num in local_ver_set:
                    continue
                all_versions.append({
                    "version": ver_num,
                    "name": rinfo.get("name", f"v{ver_num}"),
                    "changes": rinfo.get("changes", []),
                    "build_time": rinfo.get("build_time", rinfo.get("date", "")),
                    "git_commit": rinfo.get("git_commit", ""),
                    "available": ver_num in exe_versions,
                    "exe_info": exe_versions.get(ver_num),
                    "is_remote_new": True,
                })

            for ver, exe in exe_versions.items():
                if ver not in local_ver_set:
                    all_versions.append({
                        "version": ver,
                        "name": exe["filename"],
                        "changes": [],
                        "build_time": "",
                        "git_commit": "",
                        "available": True,
                        "exe_info": exe,
                        "is_remote_new": False,
                    })

            all_versions.sort(key=lambda x: x["version"], reverse=True)

            def update_ui():
                if self._ver_stable_container is not None and self._ver_stable_container.winfo_exists():
                    self._render_stable_versions(all_versions, current_version)
                if self._ver_git_container is not None and self._ver_git_container.winfo_exists():
                    self._render_git_history(git_commits)
                if self._ver_info_label is not None and self._ver_info_label.winfo_exists():
                    has_update = remote_latest and remote_latest != VERSION and remote_latest not in exe_versions
                    if has_update:
                        self._ver_info_label.configure(text=f"🆕 发现新版本 v{remote_latest}")
                    else:
                        self._ver_info_label.configure(text="✅ 已是最新版本")
                if self._ver_status_label is not None and self._ver_status_label.winfo_exists():
                    self._ver_status_label.configure(text=f"稳定版 {len(all_versions)} 个 | Git提交 {len(git_commits)} 条")

            self.root.after(0, update_ui)
        except Exception as e:
            self.root.after(0, lambda: self._ver_status_label.configure(text=f"检查失败: {e}") if self._ver_status_label is not None and self._ver_status_label.winfo_exists() else None)

    def _switch_to_exe(self, exe_path, git_commit=""):
        if not os.path.exists(exe_path):
            messagebox.showerror("错误", f"版本文件不存在:\n{exe_path}")
            return

        dev_dir = self._get_dev_dir()
        exe_filename = os.path.basename(exe_path)
        dev_exe_path = os.path.join(dev_dir, exe_filename)

        try:
            import shutil
            shutil.copy2(exe_path, dev_exe_path)
        except Exception:
            dev_exe_path = exe_path

        if git_commit and self._is_git_repo():
            r = self._run_git("stash")
            stashed = r["ok"] and "Saved" in r["stdout"]
            r = self._run_git("checkout", git_commit, timeout=30)
            if not r["ok"]:
                if stashed:
                    self._run_git("stash", "pop")
            else:
                if stashed:
                    self._run_git("stash", "pop")

        current_pid = os.getpid()
        cmd = f'ping -n 3 127.0.0.1 >nul & start "" "{dev_exe_path}"'
        subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

        self.root.destroy()

    def _switch_git_commit(self, commit_hash):
        if not self._is_git_repo():
            messagebox.showerror("错误", "不是 Git 仓库，无法切换版本")
            return

        r = self._run_git("stash")
        stashed = r["ok"] and "Saved" in r["stdout"]

        r = self._run_git("checkout", commit_hash, timeout=60)
        if not r["ok"]:
            messagebox.showerror("切换失败", f"Git checkout 失败:\n{r['stderr'][:200]}")
            if stashed:
                self._run_git("stash", "pop")
            return

        if stashed:
            self._run_git("stash", "pop")

        dev_dir = self._get_dev_dir()
        active_exe = os.path.join(dev_dir, "云集智能文件清理专家.exe")
        if os.path.exists(active_exe):
            current_pid = os.getpid()
            cmd = f'ping -n 3 127.0.0.1 >nul & start "" "{active_exe}"'
            subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.root.destroy()
        else:
            messagebox.showinfo("切换成功", f"已切换到 commit {commit_hash}\n请重启软件以加载新版本。")
            self._refresh_git_history()

    def _do_verify_and_build_report_bg(self):
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

        cat_sizes = {}
        cat_counts = {}
        for fi in self.filtered_files:
            cat = fi.get("category", "其他")
            cat_sizes[cat] = cat_sizes.get(cat, 0) + fi["size"]
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
        total_size = sum(cat_sizes.values())
        total_count = sum(cat_counts.values())

        stats_text = f"总文件数: {total_count}    总大小: {self._format_bytes(total_size)}"
        if removed > 0 or changed > 0:
            stats_text += f"\n校验: 有效 {len(valid)} | 已删除 {removed} | 已变更 {changed}"

        advice_lines = []
        sorted_cats = sorted(cat_sizes.items(), key=lambda x: x[1], reverse=True)
        if sorted_cats:
            idx = 1
            top_cat, top_size = sorted_cats[0]
            advice_lines.append(f"{idx}. {top_cat} 占比最大 ({self._format_bytes(top_size)})")
            if top_size > 1024 * 1024 * 1024:
                advice_lines.append(f"   → 建议优先清理，可释放 >1GB")
            elif top_size > 100 * 1024 * 1024:
                advice_lines.append(f"   → 建议清理，可释放 >100MB")
            idx += 1
            if cat_counts.get("duplicates", 0) > 0:
                advice_lines.append(f"{idx}. 发现 {cat_counts['duplicates']} 个重复文件 → 使用'重复检测'去重")
                idx += 1
            if cat_counts.get("empty_folders", 0) > 10:
                advice_lines.append(f"{idx}. 发现 {cat_counts['empty_folders']} 个空文件夹 → 可安全批量删除")
                idx += 1
            if cat_counts.get("cache", 0) + cat_counts.get("sys_cache", 0) > 50:
                advice_lines.append(f"{idx}. 缓存文件较多 → 建议定期清理缓存")
                idx += 1
        advice_lines.append("\n⚠️ 清理前建议备份重要文件 | 系统文件谨慎处理 | 建议使用'删除到回收站'")

        def update_ui():
            if removed > 0 or changed > 0:
                self.file_list = valid
                self.filtered_files = valid[:]
                self.total_size = sum(fi["size"] for fi in valid)
                for fi in valid:
                    self._file_size_map[fi["path"]] = fi["size"]
                self._recompute_selected_size()
                self._auto_save_results()
                self.status_label.configure(text=f"✅ 校验完成 | 有效:{len(valid)} 删除:{removed} 变更:{changed}")
            if hasattr(self, '_report_stats_label') and self._report_stats_label:
                self._report_stats_label.configure(text=stats_text)
            if hasattr(self, '_report_advice_label') and self._report_advice_label:
                self._report_advice_label.configure(text="\n".join(advice_lines))
            if hasattr(self, '_report_chart') and self._report_chart:
                self._draw_report_pie(self._report_chart)

        self.root.after(0, update_ui)

    def setup_table_area(self):
        table_frame = ctk.CTkFrame(self.main_frame, fg_color=COLOR_BG, border_width=0)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(2, 0))

        tree_container = tk.Frame(table_frame, bg=COLOR_BG)
        tree_container.pack(fill="both", expand=True)
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)

        columns = ("选择", "文件名", "完整路径", "大小", "修改时间", "类型", "分类")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15, style="Dark.Treeview",
                                yscrollcommand=self._on_yscroll, xscrollcommand=self._on_xscroll)
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.scrollbar_y = ctk.CTkScrollbar(tree_container, orientation="vertical",
                                             command=self.tree.yview,
                                             fg_color="#1a1a1a", button_color="#3a3a3a",
                                             button_hover_color="#4a4a4a", corner_radius=4,
                                             width=8)
        self.scrollbar_x = ctk.CTkScrollbar(tree_container, orientation="horizontal",
                                             command=self.tree.xview,
                                             fg_color="#1a1a1a", button_color="#3a3a3a",
                                             button_hover_color="#4a4a4a", corner_radius=4,
                                             height=8)

        self.tree.heading("选择", text="☑", command=self.toggle_select_all)
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

    def _draw_report_pie(self, canvas):
        name_to_id = {}
        for cid, cinfo in CATEGORY_TREE.items():
            name_to_id[cinfo["name"]] = cid
        name_to_id["自定义规则"] = "custom"
        name_to_id["空文件夹"] = "empty_folders"
        name_to_id["重复文件"] = "duplicates"
        name_to_id["✅保留"] = "duplicates"

        cat_sizes = {}
        for fi in self.filtered_files:
            cat = fi.get("category", "其他")
            cat_sizes[cat] = cat_sizes.get(cat, 0) + fi["size"]
        sorted_cats = sorted(cat_sizes.items(), key=lambda x: x[1], reverse=True)
        if not sorted_cats:
            canvas.create_text(110, 100, text="暂无数据", fill=COLOR_DIM, font=("Microsoft YaHei UI", 14))
            self._populate_legend([], 0, name_to_id)
            return
        top_cats = sorted_cats[:8]
        other_size = sum(s for _, s in sorted_cats[8:])
        if other_size > 0:
            top_cats.append(("其他", other_size))
        total = sum(s for _, s in top_cats)

        def get_cat_color(cat_name):
            cid = name_to_id.get(cat_name, "")
            if cid:
                return self.category_colors.get(cid, "#333333")
            return "#333333"

        canvas.delete("all")
        cx, cy, r = 110, 100, 90
        start_angle = 90
        for i, (cat, size) in enumerate(top_cats):
            extent = (size / total) * 360 if total > 0 else 0
            color = get_cat_color(cat)
            canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                            start=start_angle, extent=extent,
                            fill=color, outline="#2a2a2a", width=2, style="pieslice")
            mid_angle = start_angle + extent / 2
            if extent > 10:
                pct = (size / total) * 100
                tx = cx + (r * 0.6) * math.cos(math.radians(mid_angle))
                ty = cy - (r * 0.6) * math.sin(math.radians(mid_angle))
                canvas.create_text(tx, ty, text=f"{pct:.0f}%", fill="white", font=("Microsoft YaHei UI", 9, "bold"))
            start_angle += extent

        self._populate_legend(top_cats, total, name_to_id)

    def _populate_legend(self, top_cats, total, name_to_id):
        if not hasattr(self, '_report_legend_frame') or not self._report_legend_frame:
            return
        try:
            if not self._report_legend_frame.winfo_exists():
                return
        except Exception:
            return
        for child in self._report_legend_frame.winfo_children():
            child.destroy()

        def get_cat_color(cat_name):
            cid = name_to_id.get(cat_name, "")
            if cid:
                return self.category_colors.get(cid, "#333333")
            return "#333333"

        def get_cat_text_color(cat_name):
            cid = name_to_id.get(cat_name, "")
            if cid:
                return CATEGORY_TEXT_COLORS.get(cid, COLOR_TEXT)
            return COLOR_TEXT

        for i, (cat, size) in enumerate(top_cats):
            color = get_cat_color(cat)
            text_color = get_cat_text_color(cat)
            pct = (size / total) * 100 if total > 0 else 0

            row = ctk.CTkFrame(self._report_legend_frame, fg_color="#2a2a2a", corner_radius=6, height=32)
            row.pack(fill="x", pady=(1, 1), padx=2)
            row.pack_propagate(False)

            indicator = ctk.CTkFrame(row, fg_color=color, corner_radius=3, width=6)
            indicator.pack(side="left", padx=(6, 4), pady=7)
            indicator.pack_propagate(False)

            name_label = ctk.CTkLabel(row, text=cat, font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
                                       text_color=text_color, width=66, anchor="w")
            name_label.pack(side="left", padx=(0, 4), pady=4)

            bar_bg = ctk.CTkFrame(row, fg_color="#1a1a1a", corner_radius=3, height=8, width=56)
            bar_bg.pack(side="left", padx=(0, 4), pady=4)
            bar_bg.pack_propagate(False)

            bar_w = max(2, int(56 * pct / 100))
            bar_fill = ctk.CTkFrame(bar_bg, fg_color=color, corner_radius=3, width=bar_w, height=8)
            bar_fill.pack(side="left", padx=0, pady=0)
            bar_fill.pack_propagate(False)

            pct_label = ctk.CTkLabel(row, text=f"{pct:.1f}%", font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                                      text_color=text_color, width=44, anchor="e")
            pct_label.pack(side="left", padx=(0, 4), pady=4)

            size_label = ctk.CTkLabel(row, text=self._format_bytes(size), font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                                       text_color=COLOR_DIM, width=56, anchor="e")
            size_label.pack(side="left", padx=(0, 6), pady=4)

    def _format_bytes(self, size_bytes):
        if size_bytes == 0: return "0 B"
        names = ['B', 'KB', 'MB', 'GB', 'TB']
        i = 0
        while size_bytes >= 1024 and i < len(names) - 1:
            size_bytes /= 1024; i += 1
        return f"{round(size_bytes, 2)} {names[i]}"

    def _on_yscroll(self, first, last):
        self.scrollbar_y.set(float(first), float(last))
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.scrollbar_y.grid_remove()
        else:
            self.scrollbar_y.grid(row=0, column=1, sticky="ns")

    def _on_xscroll(self, first, last):
        self.scrollbar_x.set(float(first), float(last))
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.scrollbar_x.grid_remove()
        else:
            self.scrollbar_x.grid(row=1, column=0, sticky="ew")

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
        self.status_frame = ctk.CTkFrame(self.main_frame, fg_color=COLOR_BG, border_width=0)
        self.status_frame.pack(side="bottom", fill="x", padx=10, pady=(2, 4))
        status_info = ctk.CTkFrame(self.status_frame, fg_color=COLOR_BG)
        status_info.pack(fill="x", padx=5, pady=2)
        self.status_label = ctk.CTkLabel(status_info, text="✅ 准备就绪", anchor="w",
                                       font=ctk.CTkFont(family=FONT_FAMILY, weight="bold"), text_color=COLOR_TEXT)
        self.status_label.pack(side="left", fill="x", expand=True, padx=5)

        btn_row = ctk.CTkFrame(status_info, fg_color=COLOR_BG)
        btn_row.pack(side="right", padx=5)
        ctk.CTkButton(btn_row, text="清空列表", width=70, height=26, fg_color="#333", hover_color="#555",
                     text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                     command=self.clear_file_list).pack(side="left", padx=2)
        ctk.CTkButton(btn_row, text="保存进度", width=70, height=26, fg_color="#333", hover_color="#555",
                     text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                     command=self.save_current_progress).pack(side="left", padx=2)
        ctk.CTkButton(btn_row, text="恢复进度", width=70, height=26, fg_color="#333", hover_color="#555",
                     text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                     command=self._show_restore_menu).pack(side="left", padx=2)

        self.progress_label = ctk.CTkLabel(status_info, text="", anchor="e", font=ctk.CTkFont(family=FONT_FAMILY, size=12), text_color=COLOR_TEXT)
        self.progress_label.pack(side="right", padx=5)
        self.progress_bar = ctk.CTkProgressBar(self.status_frame, height=8, fg_color=COLOR_BORDER, progress_color=COLOR_RED)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 2))
        self.progress_bar.set(0)
        count_row = ctk.CTkFrame(self.status_frame, fg_color=COLOR_BG)
        count_row.pack(fill="x", padx=5, pady=2)
        self.count_label = ctk.CTkLabel(count_row, text="📊 文件: 0 | 总大小: 0 MB", anchor="w",
                                       text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=12))
        self.count_label.pack(side="left", padx=5)
        self.selected_size_label = ctk.CTkLabel(count_row, text="☑ 已选: 0 个 | 已选大小: 0 MB", anchor="e",
                                               text_color=COLOR_RED_LIGHT, font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"))
        self.selected_size_label.pack(side="right", padx=5)

    def _update_selected_size_display(self):
        count = len(self.selected_files)
        sel_size = self.selected_size
        self.selected_size_label.configure(text=f"☑ 已选: {count} 个 | 已选大小: {round(sel_size / (1024*1024), 2)} MB")

    def _recompute_selected_size(self):
        self.selected_size = sum(self._file_size_map.get(fp, 0) for fp in self.selected_files)

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
        self._file_size_map[info["path"]] = info["size"]
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
        if now - self._last_auto_save_time > self._auto_save_interval:
            self._last_auto_save_time = now
            try:
                scan_dir = self.dir_entry.get().strip()
                threading.Thread(target=self._auto_save_results_bg, args=(scan_dir,), daemon=True).start()
            except Exception:
                pass

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
                self.selected_size += fi["size"]
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

    def _wait_if_paused(self):
        while self.scan_paused and not self.scan_cancelled:
            time.sleep(0.1)

    def _scan_worker(self, directory):
        if self._scan_depth >= self._max_depth:
            return
        self._scan_depth += 1
        try:
            subdirs = self._fast_scan_dir(directory)
            for entry in subdirs:
                if self.scan_cancelled:
                    return
                self._wait_if_paused()
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
        self.selected_size = 0
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
        self._update_scan_button_state("scanning")
        self.scanning = True
        self.scan_cancelled = False
        self.scan_paused = False
        self.settings["scan_directory"] = directory
        self.settings["last_scan_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_settings(self.settings)
        threading.Thread(target=self.run_scan, args=(directory,), daemon=True).start()

    def start_duplicate_scan(self):
        directory = self.dir_entry.get().strip()
        if not directory or not os.path.isdir(directory):
            messagebox.showwarning("输入错误", "请选择有效的扫描目录")
            return
        if self.scanning:
            messagebox.showwarning("提示", "请等待当前操作完成")
            return
        self.file_list.clear()
        self.filtered_files.clear()
        self.selected_files.clear()
        self.selected_size = 0
        self._pending_ui_updates.clear()
        self.total_size = 0
        self.processed_items = 0
        self._displayed_count = 0
        self._dup_groups = []
        self.clear_table()
        self.status_label.configure(text="🔍 重复检测：正在扫描文件...")
        self.progress_bar.set(0)
        self.count_label.configure(text="📊 文件: 0 | 总大小: 0 MB")
        self.selected_size_label.configure(text="☑ 已选: 0 个 | 已选大小: 0 MB")
        self._update_scan_button_state("scanning")
        self.scanning = True
        self.scan_cancelled = False
        self.scan_paused = False
        self.settings["scan_directory"] = directory
        save_settings(self.settings)
        threading.Thread(target=self._run_dup_scan, args=(directory,), daemon=True).start()

    def _run_dup_scan(self, directory):
        try:
            all_files = []
            self._scan_depth = 0

            def collect_files(d):
                if self._scan_depth >= self._max_depth or self.scan_cancelled:
                    return
                self._scan_depth += 1
                try:
                    with os.scandir(d) as it:
                        for entry in it:
                            if self.scan_cancelled:
                                return
                            self._wait_if_paused()
                            if self.scan_cancelled:
                                return
                            try:
                                if entry.is_dir(follow_symlinks=False):
                                    collect_files(entry.path)
                                elif entry.is_file(follow_symlinks=False):
                                    st = entry.stat(follow_symlinks=False)
                                    if st.st_size > 0:
                                        all_files.append({
                                            "path": entry.path, "name": entry.name,
                                            "size": st.st_size, "mtime": st.st_mtime,
                                            "type": os.path.splitext(entry.name)[1].lower()
                                        })
                            except Exception:
                                continue
                except Exception:
                    pass
                finally:
                    self._scan_depth -= 1

            collect_files(directory)
            total = len(all_files)
            if total == 0 or self.scan_cancelled:
                self.root.after(0, lambda: self.status_label.configure(text="⚠️ 未找到文件"))
                return

            self.root.after(0, lambda: self.status_label.configure(text=f"🔍 重复检测：共{total}个文件，按大小分组..."))
            size_groups = {}
            for f in all_files:
                size_groups.setdefault(f["size"], []).append(f)
            size_candidates = {sz: fs for sz, fs in size_groups.items() if len(fs) >= 2}
            candidate_count = sum(len(fs) for fs in size_candidates.values())
            self.root.after(0, lambda c=candidate_count: self.status_label.configure(text=f"🔍 重复检测：{c}个大小相同的候选文件，头部哈希比对..."))

            head_groups = {}
            processed = 0
            for sz, files in size_candidates.items():
                if self.scan_cancelled:
                    return
                self._wait_if_paused()
                if self.scan_cancelled:
                    return
                for fi in files:
                    if self.scan_cancelled:
                        return
                    self._wait_if_paused()
                    if self.scan_cancelled:
                        return
                    h = self._head_hash(fi["path"])
                    if h:
                        head_groups.setdefault((sz, h), []).append(fi)
                    processed += 1
                    if processed % 50 == 0:
                        pct = processed / candidate_count
                        self.root.after(0, lambda p=pct: self.progress_bar.set(p))

            head_candidates = {k: fs for k, fs in head_groups.items() if len(fs) >= 2}
            head_candidate_count = sum(len(fs) for fs in head_candidates.values())
            self.root.after(0, lambda c=head_candidate_count: self.status_label.configure(text=f"🔍 重复检测：{c}个头部匹配文件，全量哈希比对..."))

            dup_groups = []
            processed = 0
            for key, files in head_candidates.items():
                if self.scan_cancelled:
                    return
                self._wait_if_paused()
                if self.scan_cancelled:
                    return
                full_groups = {}
                for fi in files:
                    if self.scan_cancelled:
                        return
                    self._wait_if_paused()
                    if self.scan_cancelled:
                        return
                    fh = self._full_hash(fi["path"])
                    if fh:
                        full_groups.setdefault(fh, []).append(fi)
                    processed += 1
                    if processed % 20 == 0:
                        pct = processed / max(head_candidate_count, 1)
                        self.root.after(0, lambda p=min(pct, 1.0): self.progress_bar.set(p))

                for fh, group in full_groups.items():
                    if len(group) >= 2:
                        group.sort(key=lambda x: x["mtime"])
                        dup_groups.append(group[:])

            self._dup_groups = dup_groups
            if self.scan_cancelled:
                return

            dup_colors = ["#3a2020", "#203a20", "#20203a", "#3a3a20", "#3a203a", "#203a3a", "#2a2a3a", "#3a2a2a"]
            group_total = 0
            for gi, group in enumerate(dup_groups):
                color_key = f"dup_{gi % len(dup_colors)}"
                bg_color = dup_colors[gi % len(dup_colors)]
                self.category_colors[color_key] = bg_color
                tag_name = f"cat_{color_key}"
                self.tree.tag_configure(tag_name, background=bg_color, foreground=COLOR_TEXT)
                for fi in group:
                    is_keep = fi is group[0]
                    cat_label = "✅保留" if is_keep else "重复文件"
                    desc = f"组{gi+1}: 与 {group[0]['name']} 重复" if not is_keep else f"组{gi+1}: 保留文件"
                    info = {
                        "path": fi["path"], "name": fi["name"], "size": fi["size"],
                        "mtime": fi["mtime"], "type": fi["type"],
                        "category": cat_label, "desc": desc, "dup_group": gi
                    }
                    self.file_list.append(info)
                    self.filtered_files.append(info)
                    self.total_size += fi["size"]
                    if not is_keep:
                        self.selected_files.add(fi["path"])
                        self.selected_size += fi["size"]
                    tags = (tag_name, fi["path"])
                    self.tree.insert("", "end",
                                   values=("☑" if not is_keep else "☐", fi["name"], fi["path"],
                                          self.format_size(fi["size"]),
                                          datetime.fromtimestamp(fi["mtime"]).strftime("%Y-%m-%d %H:%M:%S"),
                                          fi["type"], cat_label),
                                   tags=tags)
                    group_total += 1

            waste_size = sum(fi["size"] for g in dup_groups for fi in g[1:])
            waste_count = sum(len(g) - 1 for g in dup_groups)
            self.progress_bar.set(1.0)
            self.count_label.configure(text=f"📊 重复组: {len(dup_groups)} | 重复文件: {waste_count} | 可释放: {self._format_bytes(waste_size)}")
            self._update_selected_size_display()
            self._auto_save_results()
            self.status_label.configure(text=f"✅ 重复检测完成 | {len(dup_groups)}组重复，可释放{self._format_bytes(waste_size)}")

            if dup_groups:
                self._show_dup_toolbar()

        except Exception as e:
            self.root.after(0, lambda: self.status_label.configure(text=f"❌ 重复检测出错: {e}"))
        finally:
            self.scanning = False
            self.root.after(0, lambda: self._update_scan_button_state("idle"))

    def _show_dup_toolbar(self):
        if self._current_panel_type == "dup_toolbar":
            return
        self._destroy_current_panel()
        panel = ctk.CTkFrame(self.main_frame, fg_color="#252525", border_color="#444", border_width=1)
        panel.pack(fill="x", padx=10, pady=(2, 2), after=self._func_frame)
        self._current_panel = panel
        self._current_panel_type = "dup_toolbar"

        header = ctk.CTkFrame(panel, fg_color="#252525")
        header.pack(fill="x", padx=10, pady=(6, 2))
        ctk.CTkLabel(header, text="🔄 重复文件处理", font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
                    text_color=COLOR_TEXT).pack(side="left", padx=(0, 10))

        btn_data = [
            ("保留最新", self._dup_keep_newest),
            ("保留最旧", self._dup_keep_oldest),
            ("保留最短路径", self._dup_keep_shortest),
            ("全选重复", self._dup_select_all),
            ("取消全选", self._dup_deselect_all),
        ]
        for text, cmd in btn_data:
            ctk.CTkButton(header, text=text, height=26, fg_color="#333", hover_color=COLOR_RED,
                         text_color=COLOR_TEXT, font=ctk.CTkFont(family=FONT_FAMILY, size=12), command=cmd).pack(side="left", padx=3)

        ctk.CTkButton(header, text="✕", width=26, height=26, fg_color="#333", hover_color=COLOR_RED,
                     text_color=COLOR_DIM, font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                     command=self._destroy_current_panel).pack(side="right")

    def _dup_keep_newest(self):
        self._dup_apply_strategy("newest")

    def _dup_keep_oldest(self):
        self._dup_apply_strategy("oldest")

    def _dup_keep_shortest(self):
        self._dup_apply_strategy("shortest")

    def _dup_apply_strategy(self, strategy):
        self.selected_files.clear()
        for gi, group in enumerate(self._dup_groups):
            if strategy == "newest":
                keep = max(group, key=lambda x: x["mtime"])
            elif strategy == "oldest":
                keep = min(group, key=lambda x: x["mtime"])
            elif strategy == "shortest":
                keep = min(group, key=lambda x: len(x["path"]))
            else:
                keep = group[0]
            for fi in group:
                if fi is not keep:
                    self.selected_files.add(fi["path"])
        self._recompute_selected_size()
        self._refresh_dup_display()

    def _dup_select_all(self):
        self.selected_files.clear()
        for group in self._dup_groups:
            for fi in group[1:]:
                self.selected_files.add(fi["path"])
        self._recompute_selected_size()
        self._refresh_dup_display()

    def _dup_deselect_all(self):
        self.selected_files.clear()
        self.selected_size = 0
        self._refresh_dup_display()

    def _refresh_dup_display(self):
        for item in self.tree.get_children():
            tags = self.tree.item(item, "tags")
            fp = tags[1] if len(tags) > 1 else tags[0]
            vals = list(self.tree.item(item, "values"))
            is_sel = fp in self.selected_files
            vals[0] = "☑" if is_sel else "☐"
            cat_idx = 6
            if is_sel:
                vals[cat_idx] = "重复文件"
            else:
                for gi, group in enumerate(self._dup_groups):
                    if any(fi["path"] == fp for fi in group):
                        if any(fi["path"] == fp and fi is group[0] for fi in group):
                            vals[cat_idx] = "✅保留"
                        else:
                            vals[cat_idx] = "重复文件"
                        break
            self.tree.item(item, values=vals)
        self._update_selected_size_display()

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
            self.root.after(0, lambda: self._update_scan_button_state("idle"))
            self.root.after(0, lambda: self.progress_bar.set(1.0))
            self._auto_save_results()

    def _update_scan_button_state(self, state):
        if state == "idle":
            self.scan_btn.configure(text="🔍 开始扫描", command=self.start_scan)
            self.scan_btn.pack(side="left", padx=3)
            self.pause_btn.pack_forget()
            self.cancel_btn.pack_forget()
        elif state == "scanning":
            self.scan_btn.pack_forget()
            self.pause_btn.configure(text="⏸ 暂停", command=self.pause_scan)
            self.pause_btn.pack(side="left", padx=3)
            self.cancel_btn.pack(side="left", padx=3)
        elif state == "paused":
            self.scan_btn.pack_forget()
            self.pause_btn.configure(text="▶ 继续", command=self.resume_scan)
            self.pause_btn.pack(side="left", padx=3)
            self.cancel_btn.pack(side="left", padx=3)

    def pause_scan(self):
        self.scan_paused = True
        self.status_label.configure(text="⏸ 扫描已暂停")
        self._update_scan_button_state("paused")

    def resume_scan(self):
        self.scan_paused = False
        self.status_label.configure(text="🔍 正在继续扫描...")
        self._update_scan_button_state("scanning")

    def cancel_scan(self):
        self.scan_cancelled = True
        self.scan_paused = False
        self.scanning = False
        self.file_list = []
        self.filtered_files = []
        self.selected_files.clear()
        self.selected_size = 0
        self.clear_table()
        self.count_label.configure(text="📊 文件: 0 | 总大小: 0 MB")
        self.selected_size_label.configure(text="☑ 已选: 0 个 | 已选大小: 0 MB")
        self.progress_bar.set(0)
        self.status_label.configure(text="✅ 已取消扫描")
        self._update_scan_button_state("idle")

    def clear_file_list(self):
        if self.scanning:
            self.scan_cancelled = True
            self.scanning = False
        self.file_list = []
        self.filtered_files = []
        self.selected_files.clear()
        self.selected_size = 0
        self.clear_table()
        self.count_label.configure(text="📊 文件: 0 | 总大小: 0 MB")
        self.selected_size_label.configure(text="☑ 已选: 0 个 | 已选大小: 0 MB")
        self.progress_bar.set(0)
        self.status_label.configure(text="✅ 列表已清空")
        self._update_scan_button_state("idle")

    def save_current_progress(self):
        if not self.file_list:
            messagebox.showinfo("提示", "当前没有扫描结果可保存")
            return
        save_dir = filedialog.askdirectory(title="选择保存目录")
        if not save_dir:
            return
        data = {
            "scan_time": self.settings.get("last_scan_time", ""),
            "scan_directory": self.settings.get("scan_directory", ""),
            "file_list": self.file_list,
            "category_colors": self.category_colors,
        }
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(save_dir, f"scan_progress_{ts}.json")
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.status_label.configure(text=f"💾 进度已保存到 {os.path.basename(save_path)}")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    def display_files(self):
        self.clear_table()
        batch = []
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
        self.selected_size = 0
        if sa:
            for fi in self.filtered_files:
                self.selected_files.add(fi["path"])
            self._recompute_selected_size()
        for item in self.tree.get_children():
            fp = self.tree.item(item, "tags")[0]
            self.tree.item(item, values=("☑" if fp in self.selected_files else "☐", *self.tree.item(item, "values")[1:]))
        self._update_selected_size_display()

    def on_item_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            fp = self.tree.item(item, "tags")[0]
            fi_size = self._file_size_map.get(fp, 0)
            if fp in self.selected_files:
                self.selected_files.remove(fp)
                self.selected_size -= fi_size
            else:
                self.selected_files.add(fp)
                self.selected_size += fi_size
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
        if not hasattr(self, '_rules_display_frame'):
            self._rules_display_frame = ctk.CTkFrame(self.merged_frame, fg_color="#1e1e1e")
        for w in self._rules_display_frame.winfo_children():
            w.destroy()
        if not self.custom_rules:
            self._rules_display_frame.pack_forget()
            return
        self._rules_display_frame.pack(fill="x", padx=8, pady=(0, 4))
        labels = {"suffix": "后缀", "regex": "正则", "name_fuzzy": "模糊名", "name_exact": "精确名"}
        for rule in self.custom_rules:
            rf = ctk.CTkFrame(self._rules_display_frame, fg_color=COLOR_BG, border_color=COLOR_BORDER, border_width=1)
            rf.pack(fill="x", padx=2, pady=1)
            ctk.CTkLabel(rf, text=f"{rule['text']} [{labels.get(rule['type'], '')}]",
                        font=ctk.CTkFont(family=FONT_FAMILY, size=11), text_color=COLOR_TEXT).pack(side="left", padx=5, pady=1)
            ctk.CTkButton(rf, text="✕", width=22, height=20, command=lambda r=rule: self.remove_custom_rule(r),
                         fg_color="#333", hover_color=COLOR_RED, text_color=COLOR_DIM, font=ctk.CTkFont(family=FONT_FAMILY, size=10)).pack(side="right", padx=3, pady=1)

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

        def do_verify():
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

            def update_ui():
                self.file_list = valid
                self.filtered_files = valid[:]
                self.total_size = sum(fi["size"] for fi in valid)
                self._file_size_map = {fi["path"]: fi["size"] for fi in valid}
                self._recompute_selected_size()
                self.display_files()
                self._auto_save_results()
                self.status_label.configure(text=f"✅ 校验完成 | 有效:{len(valid)} 删除:{removed} 变更:{changed}")

            self.root.after(0, update_ui)

        threading.Thread(target=do_verify, daemon=True).start()

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

    def _auto_save_results_bg(self, scan_dir):
        try:
            data = {
                "scan_directory": scan_dir,
                "scan_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_size": self.total_size,
                "selected_files": list(self.selected_files),
                "file_list": [{"path": fi["path"], "name": fi["name"], "size": fi["size"],
                              "mtime": fi["mtime"], "type": fi["type"], "category": fi["category"], "desc": fi["desc"]}
                             for fi in self.file_list],
            }
            save_scan_results(data)
        except Exception:
            pass

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

    def _show_restore_menu(self):
        menu = tk.Menu(self.root, tearoff=0, bg="#2a2a2a", fg=COLOR_TEXT,
                      activebackground=COLOR_RED, activeforeground=COLOR_TEXT,
                      font=(FONT_FAMILY, 11))
        has_auto = load_scan_results() is not None
        if has_auto:
            menu.add_command(label="恢复上次自动保存", command=self._restore_auto)
        else:
            menu.add_command(label="恢复上次自动保存（无数据）", state="disabled")
        menu.add_command(label="从进度文件恢复...", command=self._restore_from_file)
        menu.tk_popup(*self.root.winfo_pointerxy())

    def _restore_auto(self):
        data = load_scan_results()
        if not data:
            messagebox.showinfo("提示", "没有找到自动保存的扫描结果")
            return
        self._do_restore(data)

    def _restore_from_file(self):
        fp = filedialog.askopenfilename(title="选择进度文件", filetypes=[("JSON文件", "*.json")])
        if not fp:
            return
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            messagebox.showerror("加载失败", f"无法读取进度文件:\n{e}")
            return
        if not data.get("file_list"):
            messagebox.showinfo("提示", "进度文件中没有扫描结果")
            return
        self._do_restore(data)

    def _do_restore(self, data):
        saved = data.get("file_list", [])
        if not saved:
            messagebox.showinfo("提示", "没有可恢复的结果")
            return
        self.status_label.configure(text="📂 正在恢复扫描结果...")
        self.root.update_idletasks()

        def do_restore():
            valid = []
            for fi in saved:
                fp = fi.get("path", "")
                if fp and os.path.exists(fp):
                    valid.append(fi)
            if not valid:
                self.root.after(0, lambda: self.status_label.configure(text="📂 结果已失效，请重新扫描"))
                return

            def update_ui():
                self.file_list = valid
                self.filtered_files = valid[:]
                self.total_size = data.get("total_size", sum(fi["size"] for fi in valid))
                self.selected_files = set(data.get("selected_files", [])) & {fi["path"] for fi in valid}
                self._file_size_map = {fi["path"]: fi["size"] for fi in valid}
                self._recompute_selected_size()
                sd = data.get("scan_directory", "")
                if sd:
                    self.dir_entry.delete(0, "end")
                    self.dir_entry.insert(0, sd)
                self.display_files()
                self.status_label.configure(text=f"📂 已恢复扫描结果 ({data.get('scan_time', '')})")

            self.root.after(0, update_ui)

        threading.Thread(target=do_restore, daemon=True).start()

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
        self._recompute_selected_size()
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
