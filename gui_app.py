# -*- coding: utf-8 -*-
"""
CF Xray IP Benchmark — CustomTkinter GUI (bilingual FA/EN)
"""

from __future__ import annotations

import os
import sys
import json
import re
import threading
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional

import customtkinter as ctk
from tkinter import filedialog, messagebox

SCRIPT_DIR = Path(__file__).resolve().parent
os.chdir(SCRIPT_DIR)

# ---------------------------------------------------------------------------
# Font: Vazirmatn (Persian) + fallbacks
# ---------------------------------------------------------------------------

FONT_DIR = SCRIPT_DIR / "fonts"
VAZIR_FILES = (
    "Vazirmatn-Regular.ttf",
    "Vazirmatn[wght].ttf",
    "Vazirmatn-RD-Regular.ttf",
)


def _find_vazirmatn() -> str | None:
    """Return path to a Vazirmatn TTF if available (local or system)."""
    for name in VAZIR_FILES:
        local = FONT_DIR / name
        if local.exists():
            return str(local)
    # Common install locations
    candidates = []
    if sys.platform == "win32":
        windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
        candidates += [
            windir / "Fonts" / "Vazirmatn-Regular.ttf",
            windir / "Fonts" / "Vazirmatn.ttf",
            Path.home() / "AppData/Local/Microsoft/Windows/Fonts/Vazirmatn-Regular.ttf",
        ]
    else:
        candidates += [
            Path("/usr/share/fonts/truetype/vazirmatn/Vazirmatn-Regular.ttf"),
            Path("/usr/share/fonts/Vazirmatn-Regular.ttf"),
            Path.home() / ".fonts/Vazirmatn-Regular.ttf",
            Path.home() / ".local/share/fonts/Vazirmatn-Regular.ttf",
        ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


_VAZIR_REGISTERED = False
_VAZIR_FAMILY = "Vazirmatn"


def _register_font_file(path: str) -> bool:
    """Register a TTF with the OS for this process (Windows/Linux best-effort)."""
    global _VAZIR_REGISTERED, _VAZIR_FAMILY
    try:
        if sys.platform == "win32":
            import ctypes
            FR_PRIVATE = 0x10
            ok = ctypes.windll.gdi32.AddFontResourceExW(str(path), FR_PRIVATE, 0)
            if ok:
                _VAZIR_REGISTERED = True
                _VAZIR_FAMILY = "Vazirmatn"
                return True
        else:
            # fontconfig pick-up is system-dependent; still try family name
            _VAZIR_REGISTERED = True
            _VAZIR_FAMILY = "Vazirmatn"
            return True
    except Exception:
        pass
    return False


def ensure_vazirmatn() -> str | None:
    """Try local/system font; optionally download official static Regular."""
    found = _find_vazirmatn()
    if found:
        _register_font_file(found)
        return found
    FONT_DIR.mkdir(exist_ok=True)
    dest = FONT_DIR / "Vazirmatn-Regular.ttf"
    urls = [
        "https://github.com/rastikerdar/vazirmatn/raw/master/fonts/ttf/Vazirmatn-Regular.ttf",
        "https://github.com/rastikerdar/vazirmatn/releases/download/v33.003/Vazirmatn-Regular.ttf",
    ]
    try:
        from urllib.request import urlretrieve
        for url in urls:
            try:
                urlretrieve(url, dest)
                if dest.exists() and dest.stat().st_size > 1000:
                    _register_font_file(str(dest))
                    return str(dest)
            except Exception:
                continue
    except Exception:
        pass
    found = _find_vazirmatn()
    if found:
        _register_font_file(found)
    return found


def make_font(size: int = 13, weight: str = "normal", persian: bool = False):
    """CTkFont — Vazirmatn for Persian UI, default otherwise."""
    if persian:
        ensure_vazirmatn()
        for family in (_VAZIR_FAMILY, "Vazirmatn", "Vazirmatn RD", "Tahoma", "Segoe UI"):
            try:
                return ctk.CTkFont(family=family, size=size, weight=weight)
            except Exception:
                continue
    return ctk.CTkFont(size=size, weight=weight)



# ---------------------------------------------------------------------------
# i18n
# ---------------------------------------------------------------------------

TEXTS = {
    "en": {
        "app_title": "CF Xray IP Benchmark",
        "subtitle": "Cloudflare IP · Xray · Speed test",
        "tab_run": "Run",
        "tab_settings": "Settings",
        "tab_advanced": "Advanced",
        "tab_help": "Help",
        "files": "Input files",
        "cfip": "CF IP list",
        "cfip_hint": "IPs, CIDRs or domains (one per line)",
        "links": "Config links",
        "links_hint": "vless / vmess / trojan share-links",
        "config": "Config JSON",
        "config_hint": "Main settings file (synced with this UI)",
        "browse": "Browse",
        "quick_opts": "Quick options",
        "workers": "Workers",
        "workers_hint": "How many IPs to test at the same time",
        "max_ips": "Max IPs",
        "max_ips_hint": "0 = test all targets from the list",
        "report": "Report name",
        "report_hint": "Optional prefix for Excel / log filenames",
        "clear_temp": "Clear temp after run",
        "clear_temp_hint": "Delete temporary Xray JSON files when finished",
        "baseline": "Baseline internet test",
        "baseline_hint": "Measure your real line (no VPN) before proxy tests",
        "filter_on": "Quick filter (skip slow IPs)",
        "filter_on_hint": "Probe first; skip if dead or ping too high",
        "max_lat": "Max latency (ms)",
        "max_lat_hint": "Skip IP if first ping is above this value",
        "start": "Start Benchmark",
        "stop": "Stop",
        "results": "Open Results",
        "debug": "Debug One Config",
        "live": "Live output",
        "ready": "Ready",
        "running": "Running…",
        "stopping": "Stopping…",
        "done": "Done",
        "failed": "Failed",
        "lang": "Language",
        "save_cfg": "Save to config.json",
        "reload_cfg": "Reload from disk",
        "saved": "Settings saved.",
        "reloaded": "Settings reloaded.",
        "missing_cfip": "CF IP file not found",
        "missing_links": "Links file not found",
        "busy": "Stop the current run first.",
        "sec_display": "Display",
        "sec_tests": "Speed tests",
        "sec_relay": "Relay sites",
        "sec_scoring": "Scoring",
        "sec_ranking": "Ranking",
        "sec_timeouts": "Timeouts",
        "sec_filter": "Filter",
        "sec_excel": "Excel",
        "show_progress": "Show progress lines",
        "show_progress_hint": "Print … measuring latency … so it does not look frozen",
        "show_live": "Show live result blocks",
        "show_live_hint": "Full status card after each IP",
        "show_tables": "Show final tables",
        "show_tables_hint": "Top-N ranking tables at the end",
        "write_log": "Write log file",
        "write_log_hint": "Save a live log under logs/",
        "lat_en": "Latency test",
        "lat_en_hint": "RTT via Cloudflare trace",
        "lat_samples": "Latency samples",
        "dl_en": "Download test",
        "dl_en_hint": "Download Mbps from speed.cloudflare.com",
        "dl_bytes": "Download bytes",
        "dl_rounds": "Download rounds",
        "ul_en": "Upload test",
        "ul_en_hint": "Upload Mbps to speed.cloudflare.com",
        "ul_bytes": "Upload bytes",
        "ul_rounds": "Upload rounds",
        "relay_en": "Relay tests",
        "relay_en_hint": "Open-time to major websites through the proxy",
        "relay_samples": "Samples per site",
        "sc_web": "Web score",
        "sc_web_hint": "0–10 score focused on browsing",
        "sc_insta": "Instagram score",
        "sc_insta_hint": "0–10 score focused on Instagram",
        "sc_game": "Gaming score",
        "sc_game_hint": "0–10 score focused on low latency / jitter",
        "w_web": "Overall weight · Web",
        "w_insta": "Overall weight · Instagram",
        "w_game": "Overall weight · Gaming",
        "top_n": "Top N rows",
        "top_n_hint": "How many IPs in each Top table",
        "show_web_top": "Show Web Top table",
        "show_insta_top": "Show Instagram Top table",
        "show_game_top": "Show Gaming Top table",
        "show_overall_top": "Show Overall Top table",
        "cmp_base": "Compare with baseline",
        "cmp_base_hint": "Show vs Direct column in tables",
        "http_to": "HTTP timeout (s)",
        "http_to_hint": "Timeout for full proxy HTTP requests",
        "xray_to": "Xray startup wait (s)",
        "xray_to_hint": "Max wait for local SOCKS port",
        "qto": "Quick probe timeout (s)",
        "req_exit": "Require exit IP",
        "req_exit_hint": "Skip IP if exit IP cannot be read",
        "excel_en": "Excel export",
        "excel_en_hint": "Write results/*.xlsx when finished",
        "adv_json": "Raw config.json editor",
        "adv_hint": "Advanced: edit JSON directly. Click Apply JSON to use it.",
        "apply_json": "Apply JSON",
        "json_ok": "JSON applied to UI fields.",
        "json_err": "Invalid JSON",
        "help_title": "Help & guide",
        "top_box": "Top 5 IPs (click to copy)",
        "top_empty": "No results yet — run a benchmark first",
        "copied": "Copied to clipboard",
        "top_ping": "ping",
        "top_score": "score",
        "refresh_top": "Refresh top list",
        "edit": "Edit",
        "edit_file": "Edit file content",
        "save_file": "Save",
        "file_saved": "File saved.",
        "run_mode": "Run mode",
        "mode_ip_all": "IP scanner · all configs",
        "mode_ip_one": "IP scanner · selected config",
        "mode_config_only": "Config benchmark only",
        "mode_baseline": "Your internet only",
        "mode_cf_direct": "CF IP direct test",
        "mode_ip_all_hint": "Tests every share-link against every CF IP (full matrix). Default and most thorough mode.",
        "mode_ip_one_hint": "Pick one config from the dropdown, then benchmark all CF IPs only with that config.",
        "mode_config_only_hint": "Benchmarks each config with its original server address. The CF IP list is ignored.",
        "mode_baseline_hint": "Measures only your real internet (no VPN, no proxy, no configs). Good as a reference ceiling.",
        "mode_cf_direct_hint": "Probes CF IPs directly with TCP/HTTP (no share-link / Xray). Useful to filter dead IPs fast.",
        "select_config": "Select config",
        "select_config_hint": "Used only in «selected config» mode",
    },
    "fa": {
        "app_title": "بنچمارک آی‌پی کلادفلر اکسری",
        "subtitle": "کلادفلر · اکسری · تست سرعت",
        "tab_run": "اجرا",
        "tab_settings": "تنظیمات",
        "tab_advanced": "پیشرفته",
        "tab_help": "راهنما",
        "files": "فایل‌های ورودی",
        "cfip": "لیست آی‌پی کلادفلر",
        "cfip_hint": "آی‌پی، بازه CIDR یا دامنه (هر خط یکی)",
        "links": "لینک کانفیگ",
        "links_hint": "لینک‌های vless / vmess / trojan",
        "config": "فایل تنظیمات JSON",
        "config_hint": "فایل اصلی تنظیمات (با این صفحه همگام می‌شود)",
        "browse": "انتخاب",
        "quick_opts": "گزینه‌های سریع",
        "workers": "تعداد همزمان",
        "workers_hint": "چند آی‌پی هم‌زمان تست شوند",
        "max_ips": "سقف تعداد آی‌پی",
        "max_ips_hint": "۰ = تست همه موارد لیست",
        "report": "نام گزارش",
        "report_hint": "پیشوند اختیاری نام فایل اکسل و لاگ",
        "clear_temp": "پاک کردن temp بعد از اجرا",
        "clear_temp_hint": "حذف فایل‌های موقت کانفیگ اکسری در پایان",
        "baseline": "تست اینترنت مستقیم",
        "baseline_hint": "اندازه‌گیری خط واقعی شما (بدون VPN) قبل از پروکسی",
        "filter_on": "فیلتر سریع (رد آی‌پی کند)",
        "filter_on_hint": "اول پروب؛ اگر قطع یا پینگ بالا بود رد شود",
        "max_lat": "سقف پینگ (میلی‌ثانیه)",
        "max_lat_hint": "اگر پینگ اول از این مقدار بیشتر باشد، آی‌پی رد می‌شود",
        "start": "شروع بنچمارک",
        "stop": "توقف",
        "results": "پوشه نتایج",
        "debug": "دیباگ یک کانفیگ",
        "live": "خروجی زنده",
        "ready": "آماده",
        "running": "در حال اجرا…",
        "stopping": "در حال توقف…",
        "done": "تمام",
        "failed": "ناموفق",
        "lang": "زبان",
        "save_cfg": "ذخیره در config.json",
        "reload_cfg": "بارگذاری از دیسک",
        "saved": "تنظیمات ذخیره شد.",
        "reloaded": "تنظیمات دوباره خوانده شد.",
        "missing_cfip": "فایل لیست آی‌پی پیدا نشد",
        "missing_links": "فایل لینک‌ها پیدا نشد",
        "busy": "اول اجرای فعلی را متوقف کنید.",
        "sec_display": "نمایش",
        "sec_tests": "تست‌های سرعت",
        "sec_relay": "سایت‌های رله",
        "sec_scoring": "امتیازدهی",
        "sec_ranking": "رتبه‌بندی",
        "sec_timeouts": "تایم‌اوت‌ها",
        "sec_filter": "فیلتر",
        "sec_excel": "اکسل",
        "show_progress": "نمایش خطوط پیشرفت",
        "show_progress_hint": "پیام‌هایی مثل … measuring … تا حس هنگ ندهد",
        "show_live": "نمایش نتیجه هر آی‌پی",
        "show_live_hint": "کارت وضعیت کامل بعد از هر آی‌پی",
        "show_tables": "نمایش جداول پایانی",
        "show_tables_hint": "جداول Top-N در پایان اجرا",
        "write_log": "نوشتن فایل لاگ",
        "write_log_hint": "ذخیره لاگ زنده در پوشه logs/",
        "lat_en": "تست تأخیر (Latency)",
        "lat_en_hint": "RTT از طریق Cloudflare trace",
        "lat_samples": "تعداد نمونه تأخیر",
        "dl_en": "تست دانلود",
        "dl_en_hint": "سرعت دانلود از speed.cloudflare.com",
        "dl_bytes": "حجم دانلود (بایت)",
        "dl_rounds": "تعداد دور دانلود",
        "ul_en": "تست آپلود",
        "ul_en_hint": "سرعت آپلود به speed.cloudflare.com",
        "ul_bytes": "حجم آپلود (بایت)",
        "ul_rounds": "تعداد دور آپلود",
        "relay_en": "تست رله",
        "relay_en_hint": "زمان باز شدن سایت‌های بزرگ از طریق پروکسی",
        "relay_samples": "نمونه به ازای هر سایت",
        "sc_web": "امتیاز وب‌گردی",
        "sc_web_hint": "امتیاز ۰ تا ۱۰ متمرکز بر مرور وب",
        "sc_insta": "امتیاز اینستاگرام",
        "sc_insta_hint": "امتیاز ۰ تا ۱۰ متمرکز بر اینستاگرام",
        "sc_game": "امتیاز گیمینگ",
        "sc_game_hint": "امتیاز ۰ تا ۱۰ متمرکز بر پینگ و جیتر پایین",
        "w_web": "وزن Overall · وب",
        "w_insta": "وزن Overall · اینستاگرام",
        "w_game": "وزن Overall · گیمینگ",
        "top_n": "تعداد ردیف برتر",
        "top_n_hint": "چند آی‌پی در هر جدول Top نشان داده شود",
        "show_web_top": "جدول برتر وب",
        "show_insta_top": "جدول برتر اینستاگرام",
        "show_game_top": "جدول برتر گیمینگ",
        "show_overall_top": "جدول برتر Overall",
        "cmp_base": "مقایسه با خط مستقیم",
        "cmp_base_hint": "نمایش ستون vs Direct در جداول",
        "http_to": "تایم‌اوت HTTP (ثانیه)",
        "http_to_hint": "مهلت درخواست‌های کامل از طریق پروکسی",
        "xray_to": "صبر استارت اکسری (ثانیه)",
        "xray_to_hint": "حداکثر انتظار برای آماده شدن پورت SOCKS",
        "qto": "تایم‌اوت پروب سریع (ثانیه)",
        "req_exit": "الزام Exit IP",
        "req_exit_hint": "اگر Exit IP خوانده نشد، آی‌پی رد شود",
        "excel_en": "خروجی اکسل",
        "excel_en_hint": "نوشتن results/*.xlsx در پایان",
        "adv_json": "ویرایشگر خام config.json",
        "adv_hint": "پیشرفته: ویرایش مستقیم JSON. برای اعمال، Apply را بزنید.",
        "apply_json": "اعمال JSON",
        "json_ok": "JSON روی فیلدهای رابط اعمال شد.",
        "json_err": "JSON نامعتبر است",
        "help_title": "راهنما و آموزش",
        "top_box": "۵ آی‌پی برتر (کلیک = کپی)",
        "top_empty": "هنوز نتیجه‌ای نیست — اول بنچمارک را اجرا کنید",
        "copied": "در کلیپ‌بورد کپی شد",
        "top_ping": "پینگ",
        "top_score": "امتیاز",
        "refresh_top": "بروزرسانی لیست برتر",
        "edit": "ویرایش",
        "edit_file": "ویرایش محتوای فایل",
        "save_file": "ذخیره",
        "file_saved": "فایل ذخیره شد.",
        "run_mode": "حالت اجرا",
        "mode_ip_all": "اسکنر آی‌پی · همه کانفیگ‌ها",
        "mode_ip_one": "اسکنر آی‌پی · کانفیگ انتخابی",
        "mode_config_only": "فقط بنچمارک کانفیگ",
        "mode_baseline": "فقط اینترنت کاربر",
        "mode_cf_direct": "تست مستقیم آی‌پی کلادفلر",
        "mode_ip_all_hint": "هر کانفیگ × همه آی‌پی‌های لیست",
        "mode_ip_one_hint": "یک کانفیگ از منو × همه آی‌پی‌های لیست",
        "mode_config_only_hint": "هر کانفیگ با آدرس اصلی خودش (بدون لیست آی‌پی)",
        "mode_baseline_hint": "اندازه‌گیری خط شما بدون VPN و پروکسی",
        "mode_cf_direct_hint": "پروب مستقیم آی‌پی کلادفلر (TCP/HTTP) بدون لینک",
        "select_config": "انتخاب کانفیگ",
        "select_config_hint": "فقط در حالت «کانفیگ انتخابی» استفاده می‌شود",
    },
}

HELP_EN = """
WHAT THIS APP DOES
------------------
Swaps Cloudflare IPs into your Xray share-links, starts a local SOCKS proxy,
and measures latency, download, upload, and real-site open times.
Then ranks IPs for Web, Instagram, and Gaming (scores 0–10).

RUN MODES
---------
• IP scanner · all configs (default)
  Every share-link × every CF IP (full matrix).

• IP scanner · selected config
  Pick one config from the dropdown, then test all CF IPs with only that config.

• Config benchmark only
  Test each config with its original server address. CF IP list is ignored.

• Your internet only
  Baseline test of your real line (no VPN, no proxy, no configs).

• CF IP direct test
  Probe CF IPs with TCP/HTTP only (no share-link / no Xray). Good for filtering dead IPs.

BEFORE YOU START
----------------
1) Put share-links in links.txt (vless://, vmess://, trojan://)
2) Put targets in cfip.txt:
   - plain IP: 172.66.45.96
   - scanner line: 1181 - 0 - 172.66.170.97
   - CIDR: 172.66.170.0/24
   - domain: cdn.example.com
3) Choose a Run mode (and config if needed)
4) Adjust Settings if you want
5) Press Start Benchmark

TEST FLOW (EACH IP + CONFIG)
---------------------------
1. Build temp Xray config with that CF IP (except config-only / direct / baseline)
2. Start local SOCKS on a free port
3. Quick probe — skip if dead or ping > max_latency_ms (default 2000)
4. Full latency / download / upload (if enabled)
5. Relay pings to Google, YouTube, Instagram, GitHub, ...
6. Score and stream result to the log + Top 5 panel (live)

TOP 5 PANEL
-----------
Shows best IPs during the run (live) and after finish.
• Left-click IP → copy IP
• Right-click → copy IP / IP+ping / full line

FILES TAB
---------
• CF IP list and Links side by side
• Browse or Edit file content in a popup editor
• config.json is edited from Settings / Advanced tabs

SETTINGS & ADVANCED
-------------------
Settings: graphical toggles for display, filter, tests, relay, scoring, ranking, timeouts.
Advanced: raw config.json editor (Apply JSON / Save).

LANGUAGE
--------
FA / EN switch in the header.
Persian UI uses Vazirmatn font and right-to-left layout when available.

OUTPUT
------
results/*.xlsx     ranked Excel report
results/latest_top.json   Top list for the GUI
logs/*.log         live log
temp/              per-test Xray JSON (FAILED_*.json on errors)

SCORES (0–10)
-------------
9–10 excellent · 7–8 good · 5–6 average · 3–4 weak · 0–2 poor
Overall = weighted mix of Web + Instagram + Gaming.

CLI EXAMPLES
------------
python cf_xray_benchmark.py mode=ip_all
python cf_xray_benchmark.py mode=ip_one config_index=0
python cf_xray_benchmark.py mode=config_only
python cf_xray_benchmark.py mode=baseline_only
python cf_xray_benchmark.py mode=cf_direct workers=1 max_ips=20

TIPS
----
• Start with Workers = 1 on Windows
• Allowlist python.exe and xray.exe in antivirus
• Use Max IPs while experimenting
• Keep Clear temp OFF while debugging
• Use Debug One Config to test a single link without IP swap
"""

HELP_FA = """
این برنامه چه کار می‌کند؟
------------------------
آی‌پی‌های کلادفلر را داخل لینک کانفیگ اکسری می‌گذارد، پروکسی
SOCKS
محلی راه می‌اندازد و تأخیر، دانلود، آپلود و زمان باز شدن سایت‌های واقعی را می‌سنجد.
سپس آی‌پی‌ها را برای وب، اینستاگرام و گیمینگ رتبه‌بندی می‌کند (امتیاز ۰ تا ۱۰).

حالت‌های اجرا
-------------
• اسکنر آی‌پی · همه کانفیگ‌ها (پیش‌فرض)
  هر لینک × همه آی‌پی‌های لیست (ماتریس کامل).

• اسکنر آی‌پی · کانفیگ انتخابی
  یک کانفیگ از منوی کشویی؛ فقط همان کانفیگ با همه آی‌پی‌ها تست می‌شود.

• فقط بنچمارک کانفیگ
  هر کانفیگ با آدرس اصلی خودش. لیست آی‌پی نادیده گرفته می‌شود.

• فقط اینترنت کاربر
  تست خط واقعی شما بدون
 VPN
، پروکسی و کانفیگ.

• تست مستقیم آی‌پی کلادفلر
  پروب
 TCP/HTTP
به آی‌پی‌ها بدون لینک و بدون
 Xray
(برای رد سریع آی‌پی‌های مرده).

قبل از شروع
-----------
۱) لینک‌ها را در
 links.txt
بگذارید (
 vless://
 /
 vmess://
 /
 trojan://
)

۲) اهداف را در
 cfip.txt
بنویسید:
   - آی‌پی ساده
   - خط اسکنر
   - بازه
 CIDR
   - دامنه

۳) حالت اجرا را انتخاب کنید (و در صورت نیاز کانفیگ)

۴) در صورت تمایل تنظیمات را عوض کنید

۵) شروع بنچمارک

جریان تست
---------
۱. ساخت کانفیگ موقت اکسری با
 CF IP
۲. روشن شدن
 SOCKS
۳. پروب سریع — رد اگر قطع یا پینگ بالای سقف باشد (پیش‌فرض
 2000 ms
)
۴. تأخیر / دانلود / آپلود
۵. رله به سایت‌های بزرگ
۶. امتیازدهی و نمایش زنده در لاگ و پنل ۵ برتر

پنل ۵ آی‌پی برتر
----------------
هنگام اجرا و بعد از پایان به‌روز می‌شود.
• کلیک چپ روی آی‌پی = کپی
• راست‌کلیک = کپی آی‌پی / آی‌پی+پینگ / خط کامل

فایل‌های ورودی
--------------
لیست آی‌پی و لینک کانفیگ در یک ردیف؛ دکمه انتخاب و ویرایش محتوا.

تنظیمات و پیشرفته
-----------------
تب تنظیمات: همه گزینه‌ها گرافیکی.
تب پیشرفته: ویرایش خام
 config.json

زبان
----
سوییچ
 FA
 /
 EN
فونت فارسی
 Vazirmatn
و چیدمان راست‌چین.

خروجی‌ها
--------
results/*.xlsx
results/latest_top.json
logs/*.log
temp/

امتیاز ۰ تا ۱۰
--------------
۹–۱۰ عالی · ۷–۸ خوب · ۵–۶ متوسط · ۳–۴ ضعیف · ۰–۲ خیلی ضعیف

نکات
----
• روی ویندوز با Workers = 1 شروع کنید
• python و xray را در آنتی‌ویروس مجاز کنید
• برای آزمایش از Max IPs استفاده کنید
• برای دیباگ Clear temp را خاموش بگذارید
• Debug One برای تست یک لینک بدون تعویض آی‌پی است
"""


def deep_get(d: dict, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def deep_set(d: dict, keys: tuple, value):
    cur = d
    for k in keys[:-1]:
        if k not in cur or not isinstance(cur[k], dict):
            cur[k] = {}
        cur = cur[k]
    cur[keys[-1]] = value


DEFAULT_CFG: Dict[str, Any] = {
    "workers": 1,
    "max_ips": 0,
    "report_name": "",
    "clear_temp": False,
    "display": {
        "show_progress": True,
        "show_live_result": True,
        "show_final_tables": True,
        "write_log_file": True,
    },
    "baseline": {"enabled": True},
    "filter": {
        "enabled": True,
        "max_latency_ms": 2000,
        "quick_timeout_seconds": 3,
        "require_exit_ip": False,
    },
    "tests": {
        "latency": {"enabled": True, "samples": 5},
        "download": {"enabled": True, "bytes": 250000, "rounds": 2},
        "upload": {"enabled": True, "bytes": 80000, "rounds": 1},
    },
    "relay": {
        "enabled": True,
        "samples_per_site": 2,
        "sites": {
            "Google": {"enabled": True, "url": "https://www.google.com/generate_204"},
            "Cloudflare": {"enabled": True, "url": "https://www.cloudflare.com/cdn-cgi/trace"},
            "YouTube": {"enabled": True, "url": "https://www.youtube.com/generate_204"},
            "Instagram": {"enabled": True, "url": "https://www.instagram.com/"},
            "GitHub": {"enabled": True, "url": "https://github.com/"},
            "Microsoft": {"enabled": True, "url": "https://www.microsoft.com/"},
        },
    },
    "scoring": {
        "web": True,
        "instagram": True,
        "gaming": True,
        "overall_weights": {"web": 0.35, "instagram": 0.35, "gaming": 0.30},
    },
    "ranking": {
        "top_n": 5,
        "show_web_top": True,
        "show_instagram_top": True,
        "show_gaming_top": True,
        "show_overall_top": True,
        "compare_with_baseline": True,
    },
    "timeouts": {"http_seconds": 12, "xray_startup_seconds": 3.0},
    "paths": {
        "cfip_file": "cfip.txt",
        "links_file": "links.txt",
        "temp_dir": "temp",
        "results_dir": "results",
        "logs_dir": "logs",
    },
    "excel": {"enabled": True},
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.lang = "fa"
        self.cfg: Dict[str, Any] = deepcopy(DEFAULT_CFG)
        self.proc: Optional[subprocess.Popen] = None
        self.running = False
        self._config_backup: Optional[str] = None
        self._vars: Dict[str, Any] = {}
        self._relay_vars: Dict[str, ctk.BooleanVar] = {}
        self._ui_labels = []  # (widget, key)
        self._rtl_widgets = []  # widgets to flip anchor/justify for FA
        self._layout_rows = []
        self._path_rows = []
        self._bool_rows = []
        self._num_rows = []

        self.title("CF Xray IP Benchmark")
        self.geometry("1100x780")
        self.minsize(960, 640)

        # Preload Vazirmatn for default FA UI
        ensure_vazirmatn()

        self._load_cfg_file()
        self._build()
        self._apply_cfg_to_vars()
        self._refresh_i18n()
        try:
            self.load_top_list()
        except Exception:
            pass

    def t(self, key: str) -> str:
        return TEXTS.get(self.lang, TEXTS["en"]).get(key, key)

    # ------------------------------------------------------------------ build
    def _build(self):
        # Header
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=20, pady=(16, 8))

        self.lbl_title = ctk.CTkLabel(self.header, text="", font=ctk.CTkFont(size=22, weight="bold"))
        self.lbl_title.pack(side="left")
        self._ui_labels.append((self.lbl_title, "app_title"))

        self.lbl_sub = ctk.CTkLabel(self.header, text="", text_color="gray70", font=ctk.CTkFont(size=13))
        self.lbl_sub.pack(side="left", padx=(12, 0), pady=(6, 0))
        self._ui_labels.append((self.lbl_sub, "subtitle"))

        self.status_var = ctk.StringVar(value="")
        self.lbl_status = ctk.CTkLabel(self.header, textvariable=self.status_var, text_color="gray60")
        self.lbl_status.pack(side="right")

        lang_fr = ctk.CTkFrame(self.header, fg_color="transparent")
        lang_fr.pack(side="right", padx=(0, 16))
        self.lbl_lang = ctk.CTkLabel(lang_fr, text="")
        self.lbl_lang.pack(side="left", padx=(0, 6))
        self._ui_labels.append((self.lbl_lang, "lang"))
        self.lang_seg = ctk.CTkSegmentedButton(
            lang_fr, values=["FA", "EN"], command=self._on_lang, width=100
        )
        self.lang_seg.set("FA")
        self.lang_seg.pack(side="left")

        # Tabs
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        self.tab_run = self.tabs.add("Run")
        self.tab_set = self.tabs.add("Settings")
        self.tab_adv = self.tabs.add("Advanced")
        self.tab_help = self.tabs.add("Help")
        self._tab_name_keys = {
            "Run": "tab_run",
            "Settings": "tab_settings",
            "Advanced": "tab_advanced",
            "Help": "tab_help",
        }

        self._build_run_tab()
        self._build_settings_tab()
        self._build_advanced_tab()
        self._build_help_tab()

    def _side(self) -> str:
        return "right" if self.lang == "fa" else "left"

    def _anchor(self) -> str:
        return "e" if self.lang == "fa" else "w"

    def _justify(self) -> str:
        return "right" if self.lang == "fa" else "left"

    def _pack_row(self, parent) -> "ctk.CTkFrame":
        fr = ctk.CTkFrame(parent, fg_color="transparent")
        fr.pack(fill="x", pady=3)
        self._layout_rows.append(fr)
        return fr

    def _labeled_path(self, parent, key_label, key_hint, var_name, editable: bool = False):
        fr = ctk.CTkFrame(parent, fg_color="transparent")
        fr.pack(fill="x", pady=6)
        self._layout_rows.append(fr)

        top = ctk.CTkFrame(fr, fg_color="transparent")
        top.pack(fill="x")
        self._layout_rows.append(top)

        lab = ctk.CTkLabel(top, text="", anchor=self._anchor(), font=ctk.CTkFont(weight="bold"))
        hint = ctk.CTkLabel(top, text="", anchor=self._anchor(), text_color="gray60", font=ctk.CTkFont(size=12))
        self._ui_labels.append((lab, key_label))
        self._ui_labels.append((hint, key_hint))
        self._rtl_widgets.extend([lab, hint])

        rowf = ctk.CTkFrame(fr, fg_color="transparent")
        rowf.pack(fill="x", pady=(4, 0))
        self._layout_rows.append(rowf)

        var = ctk.StringVar(value="")
        self._vars[var_name] = var
        entry = ctk.CTkEntry(rowf, textvariable=var, justify=self._justify())
        self._rtl_widgets.append(entry)

        btn_browse = ctk.CTkButton(rowf, text="", width=90, command=lambda v=var: self._browse(v))
        self._ui_labels.append((btn_browse, "browse"))

        btn_edit = None
        if editable:
            btn_edit = ctk.CTkButton(
                rowf, text="", width=90, fg_color="gray30",
                command=lambda v=var, k=key_label: self._edit_file_content(v, k),
            )
            self._ui_labels.append((btn_edit, "edit"))

        # pack order depends on language (repacked in _apply_layout)
        widgets = {"top": top, "lab": lab, "hint": hint, "rowf": rowf, "entry": entry, "browse": btn_browse, "edit": btn_edit}
        self._path_rows.append(widgets)
        self._apply_path_row_layout(widgets)
        return var

    def _apply_path_row_layout(self, w: dict):
        side = self._side()
        anc = self._anchor()
        just = self._justify()
        for child in w["top"].winfo_children():
            child.pack_forget()
        for child in w["rowf"].winfo_children():
            child.pack_forget()
        try:
            w["lab"].configure(anchor=anc)
            w["hint"].configure(anchor=anc)
            w["entry"].configure(justify=just)
        except Exception:
            pass
        if side == "right":
            w["lab"].pack(side="right")
            w["hint"].pack(side="right", padx=(0, 10))
            w["browse"].pack(side="right", padx=(6, 0))
            if w["edit"] is not None:
                w["edit"].pack(side="right", padx=(6, 0))
            w["entry"].pack(side="right", fill="x", expand=True, padx=(0, 6))
        else:
            w["lab"].pack(side="left")
            w["hint"].pack(side="left", padx=(10, 0))
            w["entry"].pack(side="left", fill="x", expand=True, padx=(0, 8))
            if w["edit"] is not None:
                w["edit"].pack(side="left", padx=(0, 6))
            w["browse"].pack(side="left")

    def _bool_row(self, parent, key_label, key_hint, var_name, default=False):
        fr = self._pack_row(parent)
        var = ctk.BooleanVar(value=default)
        self._vars[var_name] = var
        cb = ctk.CTkCheckBox(fr, text="", variable=var)
        hint = ctk.CTkLabel(fr, text="", text_color="gray60", font=ctk.CTkFont(size=12), anchor=self._anchor())
        self._ui_labels.append((cb, key_label))
        self._ui_labels.append((hint, key_hint))
        self._rtl_widgets.append(hint)
        self._bool_rows.append({"fr": fr, "cb": cb, "hint": hint})
        self._apply_bool_row_layout(self._bool_rows[-1])
        return var

    def _apply_bool_row_layout(self, w: dict):
        side = self._side()
        for child in w["fr"].winfo_children():
            child.pack_forget()
        try:
            w["hint"].configure(anchor=self._anchor())
        except Exception:
            pass
        if side == "right":
            w["cb"].pack(side="right", padx=(8, 0))
            w["hint"].pack(side="right", padx=(0, 10))
        else:
            w["cb"].pack(side="left")
            w["hint"].pack(side="left", padx=(10, 0))

    def _num_row(self, parent, key_label, key_hint, var_name, default="1", width=100):
        fr = self._pack_row(parent)
        lab = ctk.CTkLabel(fr, text="", width=220, anchor=self._anchor(), font=ctk.CTkFont(weight="bold"))
        var = ctk.StringVar(value=str(default))
        self._vars[var_name] = var
        ent = ctk.CTkEntry(fr, textvariable=var, width=width, justify=self._justify())
        self._ui_labels.append((lab, key_label))
        self._rtl_widgets.extend([lab, ent])
        hint = None
        if key_hint:
            hint = ctk.CTkLabel(fr, text="", text_color="gray60", font=ctk.CTkFont(size=12), anchor=self._anchor())
            self._ui_labels.append((hint, key_hint))
            self._rtl_widgets.append(hint)
        rec = {"fr": fr, "lab": lab, "ent": ent, "hint": hint}
        self._num_rows.append(rec)
        self._apply_num_row_layout(rec)
        return var

    def _apply_num_row_layout(self, w: dict):
        side = self._side()
        for child in w["fr"].winfo_children():
            child.pack_forget()
        try:
            w["lab"].configure(anchor=self._anchor())
            w["ent"].configure(justify=self._justify())
            if w["hint"] is not None:
                w["hint"].configure(anchor=self._anchor())
        except Exception:
            pass
        if side == "right":
            w["lab"].pack(side="right", padx=(8, 0))
            w["ent"].pack(side="right", padx=(8, 0))
            if w["hint"] is not None:
                w["hint"].pack(side="right", padx=(0, 8))
        else:
            w["lab"].pack(side="left")
            w["ent"].pack(side="left", padx=(8, 8))
            if w["hint"] is not None:
                w["hint"].pack(side="left")

    def _section(self, parent, key):
        lab = ctk.CTkLabel(parent, text="", font=ctk.CTkFont(size=15, weight="bold"), anchor=self._anchor())
        lab.pack(fill="x", pady=(12, 6))
        self._ui_labels.append((lab, key))
        self._rtl_widgets.append(lab)
        box = ctk.CTkFrame(parent)
        box.pack(fill="x", pady=(0, 4))
        inner = ctk.CTkFrame(box, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)
        return inner

    def _apply_all_layouts(self):
        for w in getattr(self, "_path_rows", []):
            self._apply_path_row_layout(w)
        for w in getattr(self, "_bool_rows", []):
            self._apply_bool_row_layout(w)
        for w in getattr(self, "_num_rows", []):
            self._apply_num_row_layout(w)

        fa = self.lang == "fa"
        f_menu = make_font(13, "normal", persian=fa)
        f_hint = make_font(12, "normal", persian=fa)

        # dropdown fonts (Vazirmatn in FA)
        for menu in (getattr(self, "mode_menu", None), getattr(self, "config_menu", None)):
            if menu is None:
                continue
            try:
                menu.configure(font=f_menu)
            except Exception:
                pass
            try:
                menu.configure(dropdown_font=f_menu)
            except Exception:
                pass

        # files two-column: in FA swap visual order (links on left visual = pack right first)
        if hasattr(self, "_files_row"):
            for child in self._files_row.winfo_children():
                child.pack_forget()
            if fa:
                self._files_left.pack(side="right", fill="both", expand=True, padx=(8, 0))
                self._files_right.pack(side="right", fill="both", expand=True, padx=(0, 8))
            else:
                self._files_left.pack(side="left", fill="both", expand=True, padx=(0, 8))
                self._files_right.pack(side="left", fill="both", expand=True, padx=(8, 0))

        # mode + config columns (same row via grid)
        if hasattr(self, "_mode_row"):
            try:
                self._col_mode.grid_forget()
                self._col_cfg.grid_forget()
            except Exception:
                pass
            if fa:
                # config on the right visually first from right: mode col=1, cfg col=0
                self._col_cfg.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
                self._col_mode.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
            else:
                self._col_mode.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
                self._col_cfg.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # mode hint full text + wrap + justify
        if hasattr(self, "lbl_mode_hint"):
            try:
                self.lbl_mode_hint.configure(
                    font=f_hint,
                    anchor=self._anchor(),
                    justify=self._justify(),
                    wraplength=480,
                )
            except Exception:
                pass

        # action buttons
        if hasattr(self, "act_bar"):
            for child in self.act_bar.winfo_children():
                child.pack_forget()
            side = self._side()
            order = [self.btn_start, self.btn_stop, self.btn_results, self.btn_debug]
            if side == "right":
                for b in order:
                    b.pack(side="right", padx=(8, 0))
            else:
                for b in order:
                    b.pack(side="left", padx=(0, 8))

        # top header
        if hasattr(self, "top_hdr"):
            for child in self.top_hdr.winfo_children():
                child.pack_forget()
            if fa:
                self.btn_refresh_top.pack(side="left")
                self.lbl_top.pack(side="right")
            else:
                self.lbl_top.pack(side="left")
                self.btn_refresh_top.pack(side="right")

    def _edit_file_content(self, var: ctk.StringVar, title_key: str):
        path = Path(var.get())
        win = ctk.CTkToplevel(self)
        win.title(self.t("edit_file"))
        win.geometry("720x520")
        win.grab_set()
        fa = self.lang == "fa"
        f = make_font(13, "normal", persian=fa)
        hdr = ctk.CTkLabel(win, text=str(path), font=f, anchor=self._anchor())
        hdr.pack(fill="x", padx=12, pady=8)
        box = ctk.CTkTextbox(win, font=make_font(12, "normal", persian=fa))
        box.pack(fill="both", expand=True, padx=12, pady=4)
        try:
            if path.exists():
                box.insert("1.0", path.read_text(encoding="utf-8", errors="ignore"))
        except Exception as e:
            box.insert("1.0", f"# error reading file: {e}\n")
        bar = ctk.CTkFrame(win, fg_color="transparent")
        bar.pack(fill="x", padx=12, pady=10)

        def do_save():
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(box.get("1.0", "end-1c"), encoding="utf-8")
                messagebox.showinfo(self.t("app_title"), self.t("file_saved"))
                try:
                    if "path_links" in self._vars and str(path) == str(Path(self._vars["path_links"].get())):
                        self._refresh_config_dropdown()
                except Exception:
                    pass
                win.destroy()
            except Exception as e:
                messagebox.showerror(self.t("app_title"), str(e))

        btn_save = ctk.CTkButton(bar, text=self.t("save_file"), command=do_save)
        if self.lang == "fa":
            btn_save.pack(side="right")
        else:
            btn_save.pack(side="left")

    def _build_run_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_run)
        scroll.pack(fill="both", expand=True)

        # ---- Files: two columns (CF IP | Links) ----
        sec = self._section(scroll, "files")
        files_row = ctk.CTkFrame(sec, fg_color="transparent")
        files_row.pack(fill="x")
        left_f = ctk.CTkFrame(files_row, fg_color="transparent")
        right_f = ctk.CTkFrame(files_row, fg_color="transparent")
        left_f.pack(side="left", fill="both", expand=True, padx=(0, 8))
        right_f.pack(side="left", fill="both", expand=True, padx=(8, 0))
        self._files_row = files_row
        self._files_left = left_f
        self._files_right = right_f
        self._labeled_path(left_f, "cfip", "cfip_hint", "path_cfip", editable=True)
        self._labeled_path(right_f, "links", "links_hint", "path_links", editable=True)
        self._vars["path_cfip"].set(str(SCRIPT_DIR / "cfip.txt"))
        self._vars["path_links"].set(str(SCRIPT_DIR / "links.txt"))
        self._vars["path_config"] = ctk.StringVar(value=str(SCRIPT_DIR / "config.json"))

        # ---- Mode + config on one row ----
        sec_mode = self._section(scroll, "run_mode")
        self._mode_keys = [
            ("ip_all", "mode_ip_all"),
            ("ip_one", "mode_ip_one"),
            ("config_only", "mode_config_only"),
            ("baseline_only", "mode_baseline"),
            ("cf_direct", "mode_cf_direct"),
        ]
        self.mode_var = ctk.StringVar(value="ip_all")
        mode_row = ctk.CTkFrame(sec_mode, fg_color="transparent")
        mode_row.pack(fill="x")
        self._mode_row = mode_row
        mode_row.grid_columnconfigure(0, weight=1, uniform="mode")
        mode_row.grid_columnconfigure(1, weight=1, uniform="mode")

        col_mode = ctk.CTkFrame(mode_row, fg_color="transparent")
        col_cfg = ctk.CTkFrame(mode_row, fg_color="transparent")
        self._col_mode = col_mode
        self._col_cfg = col_cfg
        # always two columns on one row via grid
        col_mode.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        col_cfg.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        mode_values = [TEXTS["en"][k] for _, k in self._mode_keys]
        self.mode_menu = ctk.CTkOptionMenu(
            col_mode, values=mode_values, command=self._on_mode_change, width=320,
            font=make_font(13, "normal", persian=True),
        )
        self.mode_menu.pack(fill="x", pady=(0, 4))
        self.lbl_mode_hint = ctk.CTkLabel(
            col_mode, text="", text_color="gray60", anchor="w",
            font=make_font(12, "normal", persian=True), justify="left", wraplength=420,
        )
        self.lbl_mode_hint.pack(fill="x")
        self._ui_labels.append((self.lbl_mode_hint, "mode_ip_all_hint"))
        self._rtl_widgets.append(self.lbl_mode_hint)

        self.lbl_sel_cfg = ctk.CTkLabel(col_cfg, text="", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_sel_cfg.pack(fill="x")
        self._ui_labels.append((self.lbl_sel_cfg, "select_config"))
        self._rtl_widgets.append(self.lbl_sel_cfg)
        self.lbl_sel_cfg_hint = ctk.CTkLabel(col_cfg, text="", text_color="gray60", anchor="w")
        self.lbl_sel_cfg_hint.pack(fill="x")
        self._ui_labels.append((self.lbl_sel_cfg_hint, "select_config_hint"))
        self._rtl_widgets.append(self.lbl_sel_cfg_hint)
        self.config_menu = ctk.CTkOptionMenu(
            col_cfg, values=["—"], width=320,
            font=make_font(13, "normal", persian=True),
        )
        self.config_menu.pack(fill="x", pady=(4, 0))
        self._config_choices = []
        self._refresh_config_dropdown()

        # ---- Quick options: 3-column grid ----
        sec2 = self._section(scroll, "quick_opts")
        grid = ctk.CTkFrame(sec2, fg_color="transparent")
        grid.pack(fill="x")
        self._quick_grid = grid
        # Create 3 columns
        cols = [ctk.CTkFrame(grid, fg_color="transparent") for _ in range(3)]
        for i, col in enumerate(cols):
            col.pack(side="left", fill="both", expand=True, padx=(0 if i == 0 else 6, 0 if i == 2 else 6))
        self._quick_cols = cols

        # Distribute fields across 3 columns
        self._num_row(cols[0], "workers", "workers_hint", "workers", "1")
        self._num_row(cols[1], "max_ips", "max_ips_hint", "max_ips", "0")
        self._num_row(cols[2], "report", "report_hint", "report", "", width=120)

        self._bool_row(cols[0], "clear_temp", "clear_temp_hint", "clear_temp", False)
        self._bool_row(cols[1], "baseline", "baseline_hint", "baseline", True)
        self._bool_row(cols[2], "filter_on", "filter_on_hint", "filter_on", True)

        self._num_row(cols[0], "max_lat", "max_lat_hint", "max_lat", "2000")

        # Actions
        self.act_bar = ctk.CTkFrame(scroll, fg_color="transparent")
        self.act_bar.pack(fill="x", pady=12)
        self.btn_start = ctk.CTkButton(self.act_bar, text="", width=160, height=36, command=self.start)
        self._ui_labels.append((self.btn_start, "start"))
        self.btn_stop = ctk.CTkButton(
            self.act_bar, text="", width=100, height=36, fg_color="gray30", command=self.stop, state="disabled"
        )
        self._ui_labels.append((self.btn_stop, "stop"))
        self.btn_results = ctk.CTkButton(
            self.act_bar, text="", width=120, height=36, fg_color="gray30", command=self.open_results
        )
        self._ui_labels.append((self.btn_results, "results"))
        self.btn_debug = ctk.CTkButton(
            self.act_bar, text="", width=140, height=36, fg_color="gray30", command=self.run_debug
        )
        self._ui_labels.append((self.btn_debug, "debug"))
        self._apply_all_layouts()

        self.progress = ctk.CTkProgressBar(scroll, mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 8))
        self.progress.set(0)

        # Top 5
        self.top_frame = ctk.CTkFrame(scroll, border_width=1, border_color="#3A7EBF")
        self.top_frame.pack(fill="x", pady=(4, 12))
        self.top_hdr = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        self.top_hdr.pack(fill="x", padx=10, pady=(10, 4))
        self.lbl_top = ctk.CTkLabel(
            self.top_hdr, text="", anchor=self._anchor(), font=ctk.CTkFont(size=14, weight="bold")
        )
        self._ui_labels.append((self.lbl_top, "top_box"))
        self._rtl_widgets.append(self.lbl_top)
        self.btn_refresh_top = ctk.CTkButton(
            self.top_hdr, text="", width=130, height=28, fg_color="gray30", command=self.load_top_list,
        )
        self._ui_labels.append((self.btn_refresh_top, "refresh_top"))
        self.top_list_frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        self.top_list_frame.pack(fill="x", padx=8, pady=(0, 10))
        self._top_row_widgets = []
        self.lbl_top_empty = ctk.CTkLabel(
            self.top_list_frame, text="", text_color="gray60", anchor=self._anchor()
        )
        self.lbl_top_empty.pack(fill="x", padx=4, pady=8)
        self._ui_labels.append((self.lbl_top_empty, "top_empty"))
        self._rtl_widgets.append(self.lbl_top_empty)
        self._apply_all_layouts()

        self.lbl_live = ctk.CTkLabel(scroll, text="", anchor=self._anchor(), font=ctk.CTkFont(weight="bold"))
        self.lbl_live.pack(fill="x")
        self._ui_labels.append((self.lbl_live, "live"))
        self._rtl_widgets.append(self.lbl_live)
        self.log = ctk.CTkTextbox(scroll, height=220, font=ctk.CTkFont(family="Consolas", size=12))
        self.log.pack(fill="both", expand=True, pady=(4, 8))

    def _build_settings_tab(self):


        scroll = ctk.CTkScrollableFrame(self.tab_set)
        scroll.pack(fill="both", expand=True)

        # Display
        sec = self._section(scroll, "sec_display")
        self._bool_row(sec, "show_progress", "show_progress_hint", "show_progress", True)
        self._bool_row(sec, "show_live", "show_live_hint", "show_live", True)
        self._bool_row(sec, "show_tables", "show_tables_hint", "show_tables", True)
        self._bool_row(sec, "write_log", "write_log_hint", "write_log", True)

        # Filter
        sec = self._section(scroll, "sec_filter")
        self._bool_row(sec, "filter_on", "filter_on_hint", "filter_on2", True)
        self._num_row(sec, "max_lat", "max_lat_hint", "max_lat2", "2000")
        self._num_row(sec, "qto", "", "quick_to", "3")
        self._bool_row(sec, "req_exit", "req_exit_hint", "req_exit", False)

        # Tests
        sec = self._section(scroll, "sec_tests")
        self._bool_row(sec, "lat_en", "lat_en_hint", "lat_en", True)
        self._num_row(sec, "lat_samples", "", "lat_samples", "5")
        self._bool_row(sec, "dl_en", "dl_en_hint", "dl_en", True)
        self._num_row(sec, "dl_bytes", "", "dl_bytes", "250000")
        self._num_row(sec, "dl_rounds", "", "dl_rounds", "2")
        self._bool_row(sec, "ul_en", "ul_en_hint", "ul_en", True)
        self._num_row(sec, "ul_bytes", "", "ul_bytes", "80000")
        self._num_row(sec, "ul_rounds", "", "ul_rounds", "1")

        # Relay
        sec = self._section(scroll, "sec_relay")
        self._bool_row(sec, "relay_en", "relay_en_hint", "relay_en", True)
        self._num_row(sec, "relay_samples", "", "relay_samples", "2")
        sites_fr = ctk.CTkFrame(sec, fg_color="transparent")
        sites_fr.pack(fill="x", pady=4)
        for name in ("Google", "Cloudflare", "YouTube", "Instagram", "GitHub", "Microsoft"):
            v = ctk.BooleanVar(value=True)
            self._relay_vars[name] = v
            ctk.CTkCheckBox(sites_fr, text=name, variable=v).pack(side="left", padx=(0, 12))

        # Scoring
        sec = self._section(scroll, "sec_scoring")
        self._bool_row(sec, "sc_web", "sc_web_hint", "sc_web", True)
        self._bool_row(sec, "sc_insta", "sc_insta_hint", "sc_insta", True)
        self._bool_row(sec, "sc_game", "sc_game_hint", "sc_game", True)
        self._num_row(sec, "w_web", "", "w_web", "0.35")
        self._num_row(sec, "w_insta", "", "w_insta", "0.35")
        self._num_row(sec, "w_game", "", "w_game", "0.30")

        # Ranking
        sec = self._section(scroll, "sec_ranking")
        self._num_row(sec, "top_n", "top_n_hint", "top_n", "5")
        self._bool_row(sec, "show_web_top", "", "show_web_top", True)
        self._bool_row(sec, "show_insta_top", "", "show_insta_top", True)
        self._bool_row(sec, "show_game_top", "", "show_game_top", True)
        self._bool_row(sec, "show_overall_top", "", "show_overall_top", True)
        self._bool_row(sec, "cmp_base", "cmp_base_hint", "cmp_base", True)

        # Timeouts + excel
        sec = self._section(scroll, "sec_timeouts")
        self._num_row(sec, "http_to", "http_to_hint", "http_to", "12")
        self._num_row(sec, "xray_to", "xray_to_hint", "xray_to", "3.0")

        sec = self._section(scroll, "sec_excel")
        self._bool_row(sec, "excel_en", "excel_en_hint", "excel_en", True)

        # Save / reload
        bar = ctk.CTkFrame(scroll, fg_color="transparent")
        bar.pack(fill="x", pady=16)
        self.btn_save = ctk.CTkButton(bar, text="", command=self.save_cfg)
        self.btn_save.pack(side="left", padx=(0, 8))
        self._ui_labels.append((self.btn_save, "save_cfg"))
        self.btn_reload = ctk.CTkButton(bar, text="", fg_color="gray30", command=self.reload_cfg)
        self.btn_reload.pack(side="left")
        self._ui_labels.append((self.btn_reload, "reload_cfg"))

    def _build_advanced_tab(self):
        fr = ctk.CTkFrame(self.tab_adv, fg_color="transparent")
        fr.pack(fill="both", expand=True, padx=8, pady=8)
        self.lbl_adv = ctk.CTkLabel(fr, text="", anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_adv.pack(fill="x")
        self._ui_labels.append((self.lbl_adv, "adv_json"))
        self.lbl_adv_hint = ctk.CTkLabel(fr, text="", anchor="w", text_color="gray60")
        self.lbl_adv_hint.pack(fill="x", pady=(0, 6))
        self._ui_labels.append((self.lbl_adv_hint, "adv_hint"))
        self.json_box = ctk.CTkTextbox(fr, font=ctk.CTkFont(family="Consolas", size=12))
        self.json_box.pack(fill="both", expand=True)
        bar = ctk.CTkFrame(fr, fg_color="transparent")
        bar.pack(fill="x", pady=8)
        self.btn_apply_json = ctk.CTkButton(bar, text="", command=self.apply_json)
        self.btn_apply_json.pack(side="left", padx=(0, 8))
        self._ui_labels.append((self.btn_apply_json, "apply_json"))
        self.btn_save2 = ctk.CTkButton(bar, text="", command=self.save_cfg)
        self.btn_save2.pack(side="left")
        self._ui_labels.append((self.btn_save2, "save_cfg"))
        self._sync_json_box()

    def _build_help_tab(self):
        fr = ctk.CTkFrame(self.tab_help, fg_color="transparent")
        fr.pack(fill="both", expand=True, padx=8, pady=8)
        self.lbl_help = ctk.CTkLabel(fr, text="", anchor="w", font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_help.pack(fill="x", pady=(0, 8))
        self._ui_labels.append((self.lbl_help, "help_title"))
        self.help_box = ctk.CTkTextbox(fr, font=ctk.CTkFont(size=13))
        self.help_box.pack(fill="both", expand=True)
        self.help_box.insert("1.0", HELP_FA)
        self.help_box.configure(state="disabled")

    # ------------------------------------------------------------------ i18n
    def _on_lang(self, value: str):
        self.lang = "fa" if value.upper() == "FA" else "en"
        self._refresh_i18n()

    def _refresh_i18n(self):
        fa = self.lang == "fa"
        f_title = make_font(22, "bold", persian=fa)
        f_body = make_font(13, "normal", persian=fa)
        f_bold = make_font(13, "bold", persian=fa)
        f_small = make_font(12, "normal", persian=fa)
        f_help = make_font(13, "normal", persian=fa)
        f_mono = make_font(12, "normal", persian=False)  # log stays mono

        for item in self._ui_labels:
            widget, key = item[0], item[1]
            try:
                text = self.t(key)
                if isinstance(widget, ctk.CTkCheckBox):
                    widget.configure(text=text, font=f_body)
                elif isinstance(widget, ctk.CTkButton):
                    widget.configure(text=text, font=f_bold)
                elif isinstance(widget, ctk.CTkLabel):
                    # title vs body heuristic
                    if key in ("app_title", "help_title"):
                        widget.configure(text=text, font=f_title if key == "app_title" else f_bold)
                    elif key.startswith("sec_") or key in ("files", "quick_opts", "live", "adv_json"):
                        widget.configure(text=text, font=f_bold)
                    elif key.endswith("_hint") or key in ("subtitle", "adv_hint"):
                        widget.configure(text=text, font=f_small)
                    else:
                        widget.configure(text=text, font=f_body)
            except Exception:
                pass

        # RTL / LTR alignment for labels & entries
        anchor = "e" if fa else "w"
        justify = "right" if fa else "left"
        for w in self._rtl_widgets:
            try:
                w.configure(anchor=anchor)
            except Exception:
                pass
            try:
                w.configure(justify=justify)
            except Exception:
                pass

        # Header pack order: in FA put status/lang on left visually harder; flip title anchor
        try:
            self.lbl_title.configure(anchor=anchor, font=f_title)
            self.lbl_sub.configure(anchor=anchor, font=f_small)
            self.lbl_status.configure(anchor=anchor, font=f_small)
            self.lbl_lang.configure(font=f_body)
        except Exception:
            pass

        try:
            self.log.configure(font=f_mono)
        except Exception:
            pass

        self.status_var.set(self.t("ready") if not self.running else self.t("running"))
        self.help_box.configure(state="normal")
        self.help_box.delete("1.0", "end")
        self.help_box.insert("1.0", HELP_FA if fa else HELP_EN)
        self.help_box.configure(state="disabled")
        try:
            self.help_box.configure(font=f_help)
        except Exception:
            pass
        # Textbox tag for RTL is limited; right justify help content for FA
        try:
            if fa:
                self.help_box.tag_configure("rtl", justify="right")
                self.help_box.tag_add("rtl", "1.0", "end")
            else:
                self.help_box.tag_configure("ltr", justify="left")
                self.help_box.tag_add("ltr", "1.0", "end")
        except Exception:
            pass
        try:
            # refresh mode option labels
            mode_vals = [self.t(k) for _, k in self._mode_keys]
            cur_id = self.mode_var.get() if hasattr(self, "mode_var") else "ip_all"
            fa = self.lang == "fa"
            f_menu = make_font(13, "normal", persian=fa)
            self.mode_menu.configure(values=mode_vals, font=f_menu)
            try:
                self.mode_menu.configure(dropdown_font=f_menu)
            except Exception:
                pass
            self.mode_menu.set(self._mode_id_to_display(cur_id))
            try:
                self.config_menu.configure(font=f_menu)
            except Exception:
                pass
            try:
                self.config_menu.configure(dropdown_font=f_menu)
            except Exception:
                pass
            self._on_mode_change(self._mode_id_to_display(cur_id))
        except Exception:
            pass
        try:
            self._apply_all_layouts()
            self.load_top_list()
        except Exception:
            pass
        self.title(self.t("app_title"))

    # ------------------------------------------------------------------ config sync
    def _load_cfg_file(self):
        path = SCRIPT_DIR / "config.json"
        if not path.exists():
            self.cfg = deepcopy(DEFAULT_CFG)
            return
        try:
            user = json.loads(path.read_text(encoding="utf-8"))
            self.cfg = self._merge(deepcopy(DEFAULT_CFG), user)
        except Exception:
            self.cfg = deepcopy(DEFAULT_CFG)

    def _merge(self, base, override):
        out = dict(base)
        for k, v in override.items():
            if str(k).startswith("_"):
                continue
            if isinstance(v, dict) and isinstance(out.get(k), dict):
                out[k] = self._merge(out[k], v)
            else:
                out[k] = v
        return out

    def _apply_cfg_to_vars(self):
        c = self.cfg
        self._vars["workers"].set(str(c.get("workers", 1)))
        self._vars["max_ips"].set(str(c.get("max_ips", 0)))
        self._vars["report"].set(str(c.get("report_name", "") or ""))
        ct = c.get("clear_temp")
        self._vars["clear_temp"].set(bool(ct) if isinstance(ct, bool) else False)
        self._vars["baseline"].set(bool(deep_get(c, "baseline", "enabled", default=True)))
        self._vars["filter_on"].set(bool(deep_get(c, "filter", "enabled", default=True)))
        self._vars["filter_on2"].set(bool(deep_get(c, "filter", "enabled", default=True)))
        self._vars["max_lat"].set(str(deep_get(c, "filter", "max_latency_ms", default=2000)))
        self._vars["max_lat2"].set(str(deep_get(c, "filter", "max_latency_ms", default=2000)))
        self._vars["quick_to"].set(str(deep_get(c, "filter", "quick_timeout_seconds", default=3)))
        self._vars["req_exit"].set(bool(deep_get(c, "filter", "require_exit_ip", default=False)))

        self._vars["show_progress"].set(bool(deep_get(c, "display", "show_progress", default=True)))
        self._vars["show_live"].set(bool(deep_get(c, "display", "show_live_result", default=True)))
        self._vars["show_tables"].set(bool(deep_get(c, "display", "show_final_tables", default=True)))
        self._vars["write_log"].set(bool(deep_get(c, "display", "write_log_file", default=True)))

        self._vars["lat_en"].set(bool(deep_get(c, "tests", "latency", "enabled", default=True)))
        self._vars["lat_samples"].set(str(deep_get(c, "tests", "latency", "samples", default=5)))
        self._vars["dl_en"].set(bool(deep_get(c, "tests", "download", "enabled", default=True)))
        self._vars["dl_bytes"].set(str(deep_get(c, "tests", "download", "bytes", default=250000)))
        self._vars["dl_rounds"].set(str(deep_get(c, "tests", "download", "rounds", default=2)))
        self._vars["ul_en"].set(bool(deep_get(c, "tests", "upload", "enabled", default=True)))
        self._vars["ul_bytes"].set(str(deep_get(c, "tests", "upload", "bytes", default=80000)))
        self._vars["ul_rounds"].set(str(deep_get(c, "tests", "upload", "rounds", default=1)))

        self._vars["relay_en"].set(bool(deep_get(c, "relay", "enabled", default=True)))
        self._vars["relay_samples"].set(str(deep_get(c, "relay", "samples_per_site", default=2)))
        sites = deep_get(c, "relay", "sites", default={}) or {}
        for name, var in self._relay_vars.items():
            meta = sites.get(name, {})
            if isinstance(meta, dict):
                var.set(bool(meta.get("enabled", True)))
            else:
                var.set(True)

        self._vars["sc_web"].set(bool(deep_get(c, "scoring", "web", default=True)))
        self._vars["sc_insta"].set(bool(deep_get(c, "scoring", "instagram", default=True)))
        self._vars["sc_game"].set(bool(deep_get(c, "scoring", "gaming", default=True)))
        self._vars["w_web"].set(str(deep_get(c, "scoring", "overall_weights", "web", default=0.35)))
        self._vars["w_insta"].set(str(deep_get(c, "scoring", "overall_weights", "instagram", default=0.35)))
        self._vars["w_game"].set(str(deep_get(c, "scoring", "overall_weights", "gaming", default=0.30)))

        self._vars["top_n"].set(str(deep_get(c, "ranking", "top_n", default=5)))
        self._vars["show_web_top"].set(bool(deep_get(c, "ranking", "show_web_top", default=True)))
        self._vars["show_insta_top"].set(bool(deep_get(c, "ranking", "show_instagram_top", default=True)))
        self._vars["show_game_top"].set(bool(deep_get(c, "ranking", "show_gaming_top", default=True)))
        self._vars["show_overall_top"].set(bool(deep_get(c, "ranking", "show_overall_top", default=True)))
        self._vars["cmp_base"].set(bool(deep_get(c, "ranking", "compare_with_baseline", default=True)))

        self._vars["http_to"].set(str(deep_get(c, "timeouts", "http_seconds", default=12)))
        self._vars["xray_to"].set(str(deep_get(c, "timeouts", "xray_startup_seconds", default=3.0)))
        self._vars["excel_en"].set(bool(deep_get(c, "excel", "enabled", default=True)))

        # paths
        self._vars["path_cfip"].set(str(SCRIPT_DIR / str(deep_get(c, "paths", "cfip_file", default="cfip.txt"))))
        self._vars["path_links"].set(str(SCRIPT_DIR / str(deep_get(c, "paths", "links_file", default="links.txt"))))
        self._sync_json_box()

    def _vars_to_cfg(self) -> Dict[str, Any]:
        c = deepcopy(self.cfg)

        def num(name, cast=int, default=0):
            try:
                return cast(self._vars[name].get())
            except Exception:
                return default

        # sync dual fields
        if "filter_on2" in self._vars:
            self._vars["filter_on"].set(self._vars["filter_on2"].get())
        if "max_lat2" in self._vars:
            self._vars["max_lat"].set(self._vars["max_lat2"].get())

        if hasattr(self, "mode_var"):
            c["mode"] = self.mode_var.get()
            if self.mode_var.get() == "ip_one":
                sel = self.config_menu.get()
                try:
                    c["config_index"] = int(sel[1:sel.index("]")]) if sel.startswith("[") else 0
                except Exception:
                    c["config_index"] = 0
        c["workers"] = num("workers", int, 1)
        c["max_ips"] = num("max_ips", int, 0)
        c["report_name"] = self._vars["report"].get().strip()
        c["clear_temp"] = bool(self._vars["clear_temp"].get())
        deep_set(c, ("baseline", "enabled"), bool(self._vars["baseline"].get()))
        deep_set(c, ("filter", "enabled"), bool(self._vars["filter_on"].get()))
        deep_set(c, ("filter", "max_latency_ms"), num("max_lat", int, 2000))
        deep_set(c, ("filter", "quick_timeout_seconds"), num("quick_to", float, 3))
        deep_set(c, ("filter", "require_exit_ip"), bool(self._vars["req_exit"].get()))

        deep_set(c, ("display", "show_progress"), bool(self._vars["show_progress"].get()))
        deep_set(c, ("display", "show_live_result"), bool(self._vars["show_live"].get()))
        deep_set(c, ("display", "show_final_tables"), bool(self._vars["show_tables"].get()))
        deep_set(c, ("display", "write_log_file"), bool(self._vars["write_log"].get()))

        deep_set(c, ("tests", "latency", "enabled"), bool(self._vars["lat_en"].get()))
        deep_set(c, ("tests", "latency", "samples"), num("lat_samples", int, 5))
        deep_set(c, ("tests", "download", "enabled"), bool(self._vars["dl_en"].get()))
        deep_set(c, ("tests", "download", "bytes"), num("dl_bytes", int, 250000))
        deep_set(c, ("tests", "download", "rounds"), num("dl_rounds", int, 2))
        deep_set(c, ("tests", "upload", "enabled"), bool(self._vars["ul_en"].get()))
        deep_set(c, ("tests", "upload", "bytes"), num("ul_bytes", int, 80000))
        deep_set(c, ("tests", "upload", "rounds"), num("ul_rounds", int, 1))

        deep_set(c, ("relay", "enabled"), bool(self._vars["relay_en"].get()))
        deep_set(c, ("relay", "samples_per_site"), num("relay_samples", int, 2))
        for name, var in self._relay_vars.items():
            deep_set(c, ("relay", "sites", name, "enabled"), bool(var.get()))
            if not deep_get(c, "relay", "sites", name, "url"):
                defaults = DEFAULT_CFG["relay"]["sites"].get(name, {})
                deep_set(c, ("relay", "sites", name, "url"), defaults.get("url", ""))

        deep_set(c, ("scoring", "web"), bool(self._vars["sc_web"].get()))
        deep_set(c, ("scoring", "instagram"), bool(self._vars["sc_insta"].get()))
        deep_set(c, ("scoring", "gaming"), bool(self._vars["sc_game"].get()))
        deep_set(c, ("scoring", "overall_weights", "web"), num("w_web", float, 0.35))
        deep_set(c, ("scoring", "overall_weights", "instagram"), num("w_insta", float, 0.35))
        deep_set(c, ("scoring", "overall_weights", "gaming"), num("w_game", float, 0.30))

        deep_set(c, ("ranking", "top_n"), num("top_n", int, 5))
        deep_set(c, ("ranking", "show_web_top"), bool(self._vars["show_web_top"].get()))
        deep_set(c, ("ranking", "show_instagram_top"), bool(self._vars["show_insta_top"].get()))
        deep_set(c, ("ranking", "show_gaming_top"), bool(self._vars["show_game_top"].get()))
        deep_set(c, ("ranking", "show_overall_top"), bool(self._vars["show_overall_top"].get()))
        deep_set(c, ("ranking", "compare_with_baseline"), bool(self._vars["cmp_base"].get()))

        deep_set(c, ("timeouts", "http_seconds"), num("http_to", float, 12))
        deep_set(c, ("timeouts", "xray_startup_seconds"), num("xray_to", float, 3.0))
        deep_set(c, ("excel", "enabled"), bool(self._vars["excel_en"].get()))

        # paths: keep filenames if inside SCRIPT_DIR
        for key, vname in (("cfip_file", "path_cfip"), ("links_file", "path_links")):
            p = Path(self._vars[vname].get())
            if p.exists() and p.resolve().parent == SCRIPT_DIR.resolve():
                deep_set(c, ("paths", key), p.name)
            else:
                deep_set(c, ("paths", key), str(p))

        self.cfg = c
        return c

    def _sync_json_box(self):
        try:
            text = json.dumps(self.cfg, indent=2, ensure_ascii=False)
        except Exception:
            text = "{}"
        self.json_box.delete("1.0", "end")
        self.json_box.insert("1.0", text)

    def save_cfg(self):
        c = self._vars_to_cfg()
        # strip pure comment keys when saving clean runtime — keep user comments from file if possible
        path = SCRIPT_DIR / "config.json"
        try:
            path.write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            self._sync_json_box()
            messagebox.showinfo(self.t("app_title"), self.t("saved"))
        except Exception as e:
            messagebox.showerror(self.t("app_title"), str(e))

    def reload_cfg(self):
        self._load_cfg_file()
        self._apply_cfg_to_vars()
        messagebox.showinfo(self.t("app_title"), self.t("reloaded"))

    def apply_json(self):
        raw = self.json_box.get("1.0", "end").strip()
        try:
            user = json.loads(raw)
        except Exception as e:
            messagebox.showerror(self.t("json_err"), str(e))
            return
        self.cfg = self._merge(deepcopy(DEFAULT_CFG), user)
        self._apply_cfg_to_vars()
        messagebox.showinfo(self.t("app_title"), self.t("json_ok"))

    # ------------------------------------------------------------------ helpers
    def _mode_display_to_id(self, display: str) -> str:
        for mid, key in self._mode_keys:
            if self.t(key) == display or TEXTS["en"][key] == display or TEXTS["fa"][key] == display:
                return mid
        return "ip_all"

    def _mode_id_to_display(self, mid: str) -> str:
        for m, key in self._mode_keys:
            if m == mid:
                return self.t(key)
        return self.t("mode_ip_all")

    def _on_mode_change(self, display: str):
        mid = self._mode_display_to_id(display)
        self.mode_var.set(mid)
        hint_key = {
            "ip_all": "mode_ip_all_hint",
            "ip_one": "mode_ip_one_hint",
            "config_only": "mode_config_only_hint",
            "baseline_only": "mode_baseline_hint",
            "cf_direct": "mode_cf_direct_hint",
        }.get(mid, "mode_ip_all_hint")
        try:
            self.lbl_mode_hint.configure(
                text=self.t(hint_key),
                anchor=self._anchor(),
                justify=self._justify(),
                font=make_font(12, "normal", persian=(self.lang == "fa")),
            )
        except Exception:
            pass
        state = "normal" if mid == "ip_one" else "disabled"
        try:
            self.config_menu.configure(state=state)
        except Exception:
            pass

    def _refresh_config_dropdown(self):
        path = Path(self._vars.get("path_links", ctk.StringVar(value=str(SCRIPT_DIR / "links.txt"))).get())
        choices = []
        if path.exists():
            for i, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines()):
                line = line.strip()
                if not line or line.startswith("#") or "://" not in line:
                    continue
                remark = line.split("#")[-1] if "#" in line else f"config-{len(choices)+1}"
                try:
                    from urllib.parse import unquote
                    remark = unquote(remark)[:48]
                except Exception:
                    remark = remark[:48]
                choices.append(f"[{len(choices)}] {remark}")
        if not choices:
            choices = ["—"]
        self._config_choices = choices
        try:
            self.config_menu.configure(values=choices)
            self.config_menu.set(choices[0])
        except Exception:
            pass

    def _browse(self, var: ctk.StringVar):
        path = filedialog.askopenfilename(
            initialdir=str(SCRIPT_DIR),
            filetypes=[("Text/JSON", "*.txt *.json"), ("All", "*.*")],
        )
        if path:
            var.set(path)
            if "path_links" in self._vars and var is self._vars["path_links"]:
                self._refresh_config_dropdown()

    def load_top_list(self):
        """Load results/latest_top.json and render clickable rows."""
        for w in getattr(self, "_top_row_widgets", []):
            try:
                w.destroy()
            except Exception:
                pass
        self._top_row_widgets = []

        path = SCRIPT_DIR / "results" / "latest_top.json"
        items = []
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                items = data.get("top_overall") or []
            except Exception:
                items = []

        if not items:
            self.lbl_top_empty.pack(fill="x", padx=4, pady=4)
            self.lbl_top_empty.configure(text=self.t("top_empty"))
            return

        try:
            self.lbl_top_empty.pack_forget()
        except Exception:
            pass

        fa = self.lang == "fa"
        f_body = make_font(13, "normal", persian=fa)
        f_ip = make_font(14, "bold", persian=False)

        for i, item in enumerate(items[:5], 1):
            ip = str(item.get("cf_ip") or "")
            lat = item.get("lat_avg")
            score = item.get("overall", item.get("score", ""))
            remark = str(item.get("remark") or "")[:28]
            lat_s = f"{lat} ms" if lat is not None else "—"
            score_s = f"{score}/10" if score != "" and score is not None else "—"

            row = ctk.CTkFrame(self.top_list_frame, corner_radius=8)
            row.pack(fill="x", pady=3, padx=2)
            self._top_row_widgets.append(row)

            side = "right" if fa else "left"
            rank = ctk.CTkLabel(row, text=f"#{i}", width=36, font=f_body, anchor="center")
            ip_lbl = ctk.CTkLabel(
                row, text=ip, font=f_ip, text_color="#4EA1FF", cursor="hand2",
                anchor="e" if fa else "w",
            )
            ping_lbl = ctk.CTkLabel(
                row, text=f"{self.t('top_ping')}: {lat_s}", font=f_body, text_color="gray70",
                anchor="e" if fa else "w",
            )
            sc_lbl = ctk.CTkLabel(
                row, text=f"{self.t('top_score')}: {score_s}", font=f_body, text_color="gray70",
                anchor="e" if fa else "w",
            )
            rm = None
            if remark:
                rm = ctk.CTkLabel(row, text=remark, font=f_body, text_color="gray55",
                                  anchor="e" if fa else "w")

            # pack: in FA start from right → rank, ip, ping, score
            widgets_order = [rank, ip_lbl, ping_lbl, sc_lbl]
            if rm is not None:
                widgets_order.append(rm)
            for wdg in widgets_order:
                wdg.pack(side=side, padx=8, pady=8)

            ip_lbl.bind("<Button-1>", lambda e, x=ip: self.copy_text(x))
            ip_lbl.bind("<Button-3>", lambda e, x=ip, it=item: self._top_context_menu(e, x, it))
            for w in (row, rank, ping_lbl, sc_lbl):
                w.bind("<Button-3>", lambda e, x=ip, it=item: self._top_context_menu(e, x, it))
                w.bind("<Button-1>", lambda e, x=ip: self.copy_text(x))

    def _top_context_menu(self, event, ip: str, item: dict):
        import tkinter as tk
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label=f"Copy IP  ({ip})", command=lambda: self.copy_text(ip))
        line = ip
        lat = item.get("lat_avg")
        if lat is not None:
            line = f"{ip}  ping={lat}ms"
        menu.add_command(label="Copy IP + ping", command=lambda: self.copy_text(line))
        detail = (
            f"{ip} | ping={item.get('lat_avg')}ms | "
            f"overall={item.get('overall')} | dl={item.get('dl_avg')} | "
            f"{item.get('remark', '')}"
        )
        menu.add_command(label="Copy full line", command=lambda: self.copy_text(detail))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def copy_text(self, text: str):
        if not text:
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update_idletasks()
            self.set_status(self.t("copied") + f": {text}")
            self.append_log(f"[OK] {self.t('copied')}: {text}")
        except Exception as e:
            self.append_log(f"[ERR] clipboard: {e}")

    def open_results(self):
        d = SCRIPT_DIR / "results"
        d.mkdir(exist_ok=True)
        try:
            os.startfile(str(d))  # type: ignore
        except Exception:
            subprocess.Popen(["xdg-open", str(d)])

    def append_log(self, line: str):
        def _w():
            self.log.insert("end", line + "\n")
            self.log.see("end")
            try:
                self.update_idletasks()
            except Exception:
                pass
            try:
                self._ingest_live_line(line)
            except Exception:
                pass

        self.after(0, _w)

    def _ingest_live_line(self, line: str):
        """Parse streaming benchmark output and update top panel live."""
        if not hasattr(self, "_live_results"):
            self._live_results = []
            self._live_current = {}

        s = line.strip()
        # strip colorama leftovers
        s = re.sub(r"\x1b\[[0-9;]*m", "", s)

        m = re.search(r"\[(\d+)/(\d+)\]\s+([0-9a-fA-F:.]+)\s*\|", s)
        if m:
            self._live_current = {
                "cf_ip": m.group(3),
                "remark": s.split("|", 1)[-1].strip() if "|" in s else "",
                "status": "",
                "lat_avg": None,
                "overall": 0,
            }
            return

        if s.startswith("Status") and ":" in s:
            st = s.split(":", 1)[1].strip()
            if self._live_current:
                self._live_current["status"] = st
            if st.startswith("SKIP") or st.startswith("FAIL"):
                self._live_current = {}
            elif st.startswith("OK") and self._live_current.get("cf_ip"):
                # provisional live row (refined when Scores arrives)
                ip = self._live_current["cf_ip"]
                self._live_results = [r for r in self._live_results if r.get("cf_ip") != ip]
                self._live_results.append(dict(self._live_current))
                self._live_results.sort(key=lambda x: (x.get("overall") or 0, -(x.get("lat_avg") or 99999)), reverse=True)
                self._render_live_top()
            return

        if "Latency" in s and "avg=" in s and self._live_current:
            m = re.search(r"avg=([0-9.]+)", s)
            if m:
                try:
                    self._live_current["lat_avg"] = float(m.group(1))
                except Exception:
                    pass
            return

        if ("Scores" in s or "Overall=" in s) and self._live_current.get("cf_ip"):
            m = re.search(r"Overall\s*=\s*([0-9.]+)", s, re.I)
            if m:
                try:
                    self._live_current["overall"] = float(m.group(1))
                except Exception:
                    pass
            if str(self._live_current.get("status", "")).startswith("OK"):
                ip = self._live_current["cf_ip"]
                self._live_results = [r for r in self._live_results if r.get("cf_ip") != ip]
                self._live_results.append(dict(self._live_current))
                self._live_results.sort(key=lambda x: x.get("overall") or 0, reverse=True)
                self._render_live_top()
            self._live_current = {}

    def _render_live_top(self):
        items = list(getattr(self, "_live_results", []) or [])[:5]
        if not items:
            return
        for w in getattr(self, "_top_row_widgets", []):
            try:
                w.destroy()
            except Exception:
                pass
        self._top_row_widgets = []
        try:
            self.lbl_top_empty.pack_forget()
        except Exception:
            pass

        fa = self.lang == "fa"
        f_body = make_font(13, "normal", persian=fa)
        f_ip = make_font(14, "bold", persian=False)
        side = "right" if fa else "left"

        for i, item in enumerate(items, 1):
            ip = str(item.get("cf_ip") or "")
            lat = item.get("lat_avg")
            score = item.get("overall", 0)
            lat_s = f"{lat} ms" if lat is not None else "—"
            score_s = f"{score}/10"

            row = ctk.CTkFrame(self.top_list_frame, corner_radius=8)
            row.pack(fill="x", pady=3, padx=2)
            self._top_row_widgets.append(row)

            rank = ctk.CTkLabel(row, text=f"#{i}", width=36, font=f_body, anchor="center")
            ip_lbl = ctk.CTkLabel(
                row, text=ip, font=f_ip, text_color="#4EA1FF", cursor="hand2",
                anchor="e" if fa else "w",
            )
            ping_lbl = ctk.CTkLabel(
                row, text=f"{self.t('top_ping')}: {lat_s}", font=f_body, text_color="gray70",
                anchor="e" if fa else "w",
            )
            sc_lbl = ctk.CTkLabel(
                row, text=f"{self.t('top_score')}: {score_s}", font=f_body, text_color="gray70",
                anchor="e" if fa else "w",
            )
            for wdg in (rank, ip_lbl, ping_lbl, sc_lbl):
                wdg.pack(side=side, padx=8, pady=8)
            ip_lbl.bind("<Button-1>", lambda e, x=ip: self.copy_text(x))
            for w in (row, rank, ping_lbl, sc_lbl, ip_lbl):
                w.bind("<Button-3>", lambda e, x=ip, it=item: self._top_context_menu(e, x, it))

    def set_status(self, key_or_text: str):
        text = self.t(key_or_text) if key_or_text in TEXTS["en"] else key_or_text
        self.after(0, lambda: self.status_var.set(text))

    # ------------------------------------------------------------------ run
    def start(self):
        if self.running:
            return
        mode = self.mode_var.get() if hasattr(self, "mode_var") else "ip_all"
        if mode in ("ip_all", "ip_one", "cf_direct"):
            if not Path(self._vars["path_cfip"].get()).exists():
                messagebox.showerror(self.t("app_title"), self.t("missing_cfip"))
                return
        if mode in ("ip_all", "ip_one", "config_only"):
            if not Path(self._vars["path_links"].get()).exists():
                messagebox.showerror(self.t("app_title"), self.t("missing_links"))
                return

        c = self._vars_to_cfg()
        # materialize external files if needed
        for key, vname in (("cfip_file", "path_cfip"), ("links_file", "path_links")):
            src = Path(self._vars[vname].get())
            if src.exists() and src.resolve().parent != SCRIPT_DIR.resolve():
                dest = SCRIPT_DIR / f"_gui_{src.name}"
                dest.write_text(src.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
                deep_set(c, ("paths", key), dest.name)

        main_cfg = SCRIPT_DIR / "config.json"
        try:
            if main_cfg.exists():
                self._config_backup = main_cfg.read_text(encoding="utf-8")
            main_cfg.write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except Exception as e:
            messagebox.showerror(self.t("app_title"), str(e))
            return

        self.log.delete("1.0", "end")
        self._live_results = []
        self._live_current = {}
        self.running = True
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.progress.start()
        self.set_status("running")

        mode = self.mode_var.get() if hasattr(self, "mode_var") else "ip_all"
        args = [
            sys.executable, "-u", str(SCRIPT_DIR / "cf_xray_benchmark.py"),
            f"workers={int(self._vars['workers'].get() or 1)}",
            f"clear_temp={'true' if self._vars['clear_temp'].get() else 'false'}",
            f"mode={mode}",
        ]
        if mode == "ip_one":
            # parse index from "[0] remark"
            sel = self.config_menu.get() if hasattr(self, "config_menu") else "[0]"
            idx = 0
            try:
                if sel.startswith("[") and "]" in sel:
                    idx = int(sel[1:sel.index("]")])
            except Exception:
                idx = 0
            args.append(f"config_index={idx}")
        try:
            mi = int(self._vars["max_ips"].get() or 0)
        except Exception:
            mi = 0
        if mi > 0:
            args.append(f"max_ips={mi}")
        report = self._vars["report"].get().strip()
        if report:
            args.append(f"report={report}")

        def run():
            try:
                if os.name == "nt":
                    subprocess.run(
                        ["taskkill", "/F", "/IM", "xray.exe"],
                        capture_output=True,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                    )
                creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
                env = os.environ.copy()
                env["PYTHONUNBUFFERED"] = "1"
                env["PYTHONIOENCODING"] = "utf-8"
                self.proc = subprocess.Popen(
                    args, cwd=str(SCRIPT_DIR), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace", bufsize=1, env=env,
                    creationflags=creationflags,
                )
                assert self.proc.stdout is not None
                for line in self.proc.stdout:
                    self.append_log(line.rstrip("\n"))
                self.proc.wait()
                if self.proc.returncode == 0:
                    self.append_log("[OK] Done.")
                    self.set_status("done")
                else:
                    self.append_log(f"[ERR] Exit code {self.proc.returncode}")
                    self.set_status("failed")
            except Exception as e:
                self.append_log(f"[ERR] {e}")
                self.set_status("failed")
            finally:
                self._restore_config()
                self.after(0, self._finish_ui)

        threading.Thread(target=run, daemon=True).start()

    def _restore_config(self):
        try:
            if self._config_backup is not None:
                (SCRIPT_DIR / "config.json").write_text(self._config_backup, encoding="utf-8")
        except Exception:
            pass

    def _finish_ui(self):
        self.running = False
        self.proc = None
        self.progress.stop()
        self.progress.set(0)
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        try:
            self.load_top_list()
        except Exception:
            pass

    def stop(self):
        if not self.running:
            return
        self.append_log("[WARN] Stopping…")
        self.set_status("stopping")
        try:
            if self.proc and self.proc.poll() is None:
                self.proc.terminate()
                try:
                    self.proc.wait(timeout=3)
                except Exception:
                    self.proc.kill()
        except Exception:
            pass
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/IM", "xray.exe"],
                capture_output=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )

    def run_debug(self):
        if self.running:
            messagebox.showinfo(self.t("app_title"), self.t("busy"))
            return
        debug = SCRIPT_DIR / "debug_one.py"
        if not debug.exists():
            messagebox.showerror(self.t("app_title"), "debug_one.py missing")
            return
        self.log.delete("1.0", "end")
        self.running = True
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.progress.start()
        self.set_status("running")

        def run():
            try:
                creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
                env = os.environ.copy()
                env["PYTHONUNBUFFERED"] = "1"
                self.proc = subprocess.Popen(
                    [sys.executable, "-u", str(debug)], cwd=str(SCRIPT_DIR),
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                    encoding="utf-8", errors="replace", bufsize=1, env=env,
                    creationflags=creationflags,
                )
                assert self.proc.stdout is not None
                for line in self.proc.stdout:
                    self.append_log(line.rstrip("\n"))
                self.proc.wait()
                self.set_status("done" if self.proc.returncode == 0 else "failed")
            except Exception as e:
                self.append_log(f"[ERR] {e}")
                self.set_status("failed")
            finally:
                self.after(0, self._finish_ui)

        threading.Thread(target=run, daemon=True).start()


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
