# CLI Reference / مرجع خط فرمان

**CF Xray IP Benchmark** — command-line usage guide  
راهنمای اجرای پروژه از طریق خط فرمان

Language: **English** first, then **فارسی** in each section.

---

## Table of contents

1. [Quick start](#1-quick-start)
2. [Arguments](#2-arguments)
3. [Run modes](#3-run-modes)
4. [Mode details](#4-mode-details)
5. [Practical examples](#5-practical-examples)
6. [Config vs CLI priority](#6-config-vs-cli-priority)
7. [Exit codes & outputs](#7-exit-codes--outputs)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Quick start

### English

```bash
# Install dependencies
pip install -r requirements.txt

# Default run (mode=ip_all from config or built-in default)
python cf_xray_benchmark.py

# Explicit mode
python cf_xray_benchmark.py mode=ip_all workers=1
```

Windows:

```bat
setup.bat
run.bat
run.bat mode=ip_all workers=1 max_ips=10
```

### فارسی

```bash
# نصب وابستگی‌ها
pip install -r requirements.txt

# اجرای پیش‌فرض
python cf_xray_benchmark.py

# تعیین صریح حالت
python cf_xray_benchmark.py mode=ip_all workers=1
```

ویندوز:

```bat
setup.bat
run.bat
run.bat mode=ip_all workers=1 max_ips=10
```

---

## 2. Arguments

All arguments use the form `key=value` (except `custom`).

| Argument | Type | Default | English | فارسی |
|----------|------|---------|---------|--------|
| `mode` | string | `ip_all` | Run mode (see below) | حالت اجرا |
| `config_index` | int ≥ 0 | `0` | Config index in `links.txt` for `ip_one` | ایندکس کانفیگ برای حالت انتخابی |
| `workers` | int ≥ 1 | from `config.json` / `1` | Parallel tests | تعداد تست همزمان |
| `max_ips` | int ≥ 1 | all (`0` in config) | Only first N targets from `cfip.txt` | فقط N آی‌پی اول |
| `report` | string | empty | Prefix for Excel/log filenames | پیشوند نام گزارش |
| `clear_temp` | true/false | ask / config | Delete or keep `temp/` after run | پاک کردن یا نگه‌داشتن temp |
| `custom` | flag | off | Interactive prompts at start | پرسش تعاملی در شروع |

### English notes

- CLI values **override** `config.json` when the argument is present on the command line.
- Boolean `clear_temp`: `true` / `1` / `yes` or `false` / `0` / `no`.

### نکات فارسی

- اگر آرگومان روی خط فرمان باشد، روی
  `config.json`
  اولویت دارد.
- برای
  `clear_temp`
  مقادیر
  `true`
  /
  `false`
  معتبر است.

---

## 3. Run modes

| `mode=` | English name | نام فارسی |
|---------|--------------|-----------|
| `ip_all` | IP scanner · all configs (**default**) | اسکنر آی‌پی · همه کانفیگ‌ها (**پیش‌فرض**) |
| `ip_one` | IP scanner · selected config | اسکنر آی‌پی · کانفیگ انتخابی |
| `config_only` | Config benchmark only | فقط بنچمارک کانفیگ |
| `baseline_only` | Your internet only | فقط اینترنت کاربر |
| `cf_direct` | CF IP direct test | تست مستقیم آی‌پی کلادفلر |

```bash
python cf_xray_benchmark.py mode=ip_all
python cf_xray_benchmark.py mode=ip_one config_index=0
python cf_xray_benchmark.py mode=config_only
python cf_xray_benchmark.py mode=baseline_only
python cf_xray_benchmark.py mode=cf_direct
```

---

## 4. Mode details

### 4.1 `mode=ip_all` — IP scanner · all configs

**English**

- Builds a full matrix: **every** valid link in `links.txt` × **every** target in `cfip.txt`.
- For each pair, swaps the CF IP into the Xray outbound, starts local SOCKS, runs probe → latency → speed → relay → scores.
- Use when you want the complete ranking of IPs across all your configs.
- Workload size ≈ `configs × IPs` (can be large; use `max_ips` and `workers=1` first).

**Required files:** `links.txt`, `cfip.txt`

```bash
python cf_xray_benchmark.py mode=ip_all workers=1 max_ips=30
```

**فارسی**

- ماتریس کامل: هر لینک معتبر در
  `links.txt`
  × هر هدف در
  `cfip.txt`
  .
- برای هر جفت، آی‌پی کلادفلر داخل کانفیگ اکسری قرار می‌گیرد و تست کامل انجام می‌شود.
- مناسب وقتی می‌خواهید همه آی‌پی‌ها را روی همه کانفیگ‌ها مقایسه کنید.
- حجم کار ≈ تعداد کانفیگ × تعداد آی‌پی؛ اول با
  `max_ips`
  و
  `workers=1`
  شروع کنید.

**فایل‌های لازم:**
 `links.txt`
،
 `cfip.txt`

---

### 4.2 `mode=ip_one` — IP scanner · selected config

**English**

- Uses **one** config from `links.txt`, selected by `config_index` (0-based).
- Tests that config against **all** (or first `max_ips`) CF targets.
- Ideal when one working share-link is known and you only want the best CF IP for it.

**Required files:** `links.txt`, `cfip.txt`  
**Extra argument:** `config_index=N`

```bash
# First link in links.txt (index 0)
python cf_xray_benchmark.py mode=ip_one config_index=0

# Third link (index 2), limit 50 IPs
python cf_xray_benchmark.py mode=ip_one config_index=2 max_ips=50 workers=1
```

**فارسی**

- فقط **یک** کانفیگ از
  `links.txt`
  با ایندکس
  `config_index`
  (از صفر).
- همان کانفیگ روی همه (یا
  `max_ips`
  تا) آی‌پی کلادفلر تست می‌شود.
- مناسب وقتی یک لینک سالم دارید و فقط بهترین
  CF IP
  را برای همان می‌خواهید.

**فایل‌های لازم:**
 `links.txt`
،
 `cfip.txt`  
**آرگومان اضافه:**
 `config_index=N`

---

### 4.3 `mode=config_only` — Config benchmark only

**English**

- Benchmarks each share-link **with its original server address**.
- Does **not** read or use `cfip.txt`.
- Useful to compare quality of multiple configs/providers before IP scanning.

**Required files:** `links.txt` only

```bash
python cf_xray_benchmark.py mode=config_only workers=1
```

**فارسی**

- هر لینک را با **آدرس اصلی خودش** تست می‌کند.
- فایل
  `cfip.txt`
  استفاده **نمی‌شود**.
- برای مقایسه کیفیت چند کانفیگ/سرویس قبل از اسکن آی‌پی مناسب است.

**فایل لازم:** فقط
 `links.txt`

---

### 4.4 `mode=baseline_only` — Your internet only

**English**

- Measures **your direct internet** (no VPN, no Xray, no CF IP list).
- No share-link and no IP list required.
- Use as a reference ceiling: proxy results can be compared against this baseline in normal modes when `baseline.enabled` is true.

**Required files:** none (network access only)

```bash
python cf_xray_benchmark.py mode=baseline_only
```

**فارسی**

- فقط **اینترنت مستقیم** شما را می‌سنجد (بدون
  VPN
 ، بدون اکسری، بدون لیست آی‌پی).
- لینک و لیست آی‌پی لازم نیست.
- به‌عنوان سقف مرجع؛ در حالت‌های عادی هم اگر
  `baseline.enabled`
  روشن باشد، با نتایج پروکسی مقایسه می‌شود.

**فایل لازم:** ندارد (فقط شبکه)

---

### 4.5 `mode=cf_direct` — CF IP direct test

**English**

- Probes each CF target **without** any share-link or Xray process.
- Uses TCP connect to `:443` and optional HTTPS requests to the IP (CDN-style).
- Fast way to drop dead or very slow IPs before a full `ip_all` / `ip_one` run.
- Scoring still produces 0–10 style metrics from latency samples when possible.

**Required files:** `cfip.txt` only

```bash
python cf_xray_benchmark.py mode=cf_direct max_ips=100 workers=2
```

**فارسی**

- هر هدف کلادفلر را **بدون** لینک و **بدون** پروسه اکسری پروب می‌کند.
- اتصال
  TCP
  به پورت
  443
  و در صورت امکان درخواست
  HTTPS
  به خود آی‌پی.
- برای حذف سریع آی‌پی‌های مرده/خیلی کند قبل از اسکن کامل مناسب است.

**فایل لازم:** فقط
 `cfip.txt`

---

## 5. Practical examples

### English

```bash
# Safe first run on Windows
python cf_xray_benchmark.py mode=ip_one config_index=0 workers=1 max_ips=10 clear_temp=false

# Full matrix, limited IPs, named report
python cf_xray_benchmark.py mode=ip_all max_ips=25 workers=1 report=nightly

# Compare configs only
python cf_xray_benchmark.py mode=config_only clear_temp=true

# Filter CF list quickly, then deep-scan survivors later
python cf_xray_benchmark.py mode=cf_direct max_ips=200 workers=2

# Interactive prompts
python cf_xray_benchmark.py custom
```

### فارسی

```bash
# اجرای امن اولیه روی ویندوز
python cf_xray_benchmark.py mode=ip_one config_index=0 workers=1 max_ips=10 clear_temp=false

# ماتریس کامل با سقف آی‌پی و نام گزارش
python cf_xray_benchmark.py mode=ip_all max_ips=25 workers=1 report=nightly

# فقط مقایسه کانفیگ‌ها
python cf_xray_benchmark.py mode=config_only clear_temp=true

# فیلتر سریع لیست کلادفلر
python cf_xray_benchmark.py mode=cf_direct max_ips=200 workers=2

# حالت تعاملی
python cf_xray_benchmark.py custom
```

---

## 6. Config vs CLI priority

### English

1. Built-in defaults  
2. Values from `config.json`  
3. CLI `key=value` arguments (highest when present)

Relevant `config.json` keys:

```json
{
  "mode": "ip_all",
  "config_index": 0,
  "workers": 1,
  "max_ips": 0,
  "report_name": "",
  "clear_temp": null,
  "filter": {
    "enabled": true,
    "max_latency_ms": 2000,
    "quick_timeout_seconds": 3
  }
}
```

`max_ips: 0` in config means **all** IPs. On the CLI, omit `max_ips` to use config, or pass `max_ips=N` to limit.

### فارسی

1. پیش‌فرض داخلی  
2. مقادیر
   `config.json`  
3. آرگومان‌های
   CLI
   (بالاترین اولویت در صورت وجود)

`max_ips: 0`
در تنظیمات یعنی **همه** آی‌پی‌ها. در
 CLI
اگر
 `max_ips`
ندهید از تنظیمات خوانده می‌شود.

---

## 7. Exit codes & outputs

### English

| Path | Description |
|------|-------------|
| `results/*.xlsx` | Excel ranking (if enabled) |
| `results/latest_top.json` | Top list for GUI / automation |
| `logs/*.log` | Live log of the run |
| `temp/` | Per-test Xray JSON; `FAILED_*.json` on errors |

During the run, each finished test prints a block (`Status`, latency, scores).  
With the filter enabled, bad targets may appear as `SKIP (...)`.

### فارسی

| مسیر | توضیح |
|------|--------|
| `results/*.xlsx` | گزارش اکسل |
| `results/latest_top.json` | لیست برتر برای GUI |
| `logs/*.log` | لاگ زنده |
| `temp/` | کانفیگ‌های موقت؛ در خطا `FAILED_*.json` |

وضعیت‌ها:
 `OK`
 /
 `SKIP`
 /
 `FAIL`
.

---

## 8. Troubleshooting

### English

| Problem | What to try |
|---------|-------------|
| `xray exit` / port bind | `workers=1`; kill leftover `xray.exe`; allowlist in antivirus |
| All `SKIP` / high ping | Raise `filter.max_latency_ms` in config, or disable filter |
| Invalid mode | Use only: `ip_all`, `ip_one`, `config_only`, `baseline_only`, `cf_direct` |
| `config_index` out of range | Check how many non-comment links exist in `links.txt` (0-based) |
| Need one known-good link | `python debug_one.py` |

Windows:

```powershell
Get-Process xray -ErrorAction SilentlyContinue | Stop-Process -Force
```

### فارسی

| مشکل | اقدام |
|------|--------|
| خروج اکسری / اشغال پورت | `workers=1`؛ بستن `xray`؛ مجاز کردن در آنتی‌ویروس |
| همه `SKIP` | افزایش `max_latency_ms` یا خاموش کردن فیلتر |
| حالت نامعتبر | فقط پنج مقدار معتبر بالا |
| ایندکس کانفیگ نامعتبر | تعداد لینک‌های غیرکامنت در `links.txt` را بشمارید |
| تست یک لینک سالم | `python debug_one.py` |

---

## Related docs

| File | Content |
|------|---------|
| `README.md` | Full project guide (English) |
| `README_FA.md` | راهنمای کامل فارسی |
| `config.json` | All toggles with inline `_` comments |
| GUI Help tab | Same concepts inside the app |

---

## Credit

Inspired by [ExtremeDot/xray-config-benchmark](https://github.com/ExtremeDot/xray-config-benchmark).  
Proxy core: [XTLS/Xray-core](https://github.com/XTLS/Xray-core).
