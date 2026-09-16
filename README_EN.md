# CF Xray IP Benchmark

<img width="1092" height="1022" alt="image" src="https://github.com/user-attachments/assets/5521ba78-ae31-45b8-a90f-ea32df32ad55" />

Test **Cloudflare IPs** with your **Xray share-links** (`vless` / `vmess` / `trojan`), score them for **Web**, **Instagram**, and **Gaming**, and export ranked results to Excel.

Inspired by [ExtremeDot/xray-config-benchmark](https://github.com/ExtremeDot/xray-config-benchmark).

---

## Features

- Multiple **run modes** (IP matrix, single config, config-only, baseline, CF direct probe)
- Swap each CF IP into your config and test through a local Xray SOCKS5 proxy
- **Quick probe filter** — skip dead or ultra-slow IPs early (default max first ping **2000 ms**)
- **Baseline** of your real internet (no VPN) for comparison
- Latency / Download / Upload (Cloudflare speed endpoints)
- Relay open-time to Google, YouTube, Instagram, GitHub, Cloudflare, Microsoft
- Scores **0–10** for Web, Instagram, Gaming + Overall
- Live log + **live Top 5** panel (click / right-click to copy IP)
- `config.json` toggles for almost every step
- **CustomTkinter GUI** — bilingual FA/EN, RTL + Vazirmatn for Persian, graphical settings, Advanced JSON, Help tab
- Windows + Linux CLI scripts

---

## Quick start

### Windows

```bat
setup.bat
run.bat
```

**GUI:**

```bat
Windows GUI.bat
```

or:

```bat
python gui.py
```

Requires packages from `requirements.txt` (including `customtkinter`).

### Linux / macOS

```bash
chmod +x setup.sh run.sh
./setup.sh
./run.sh
python3 gui.py
```

### Manual

```bash
pip install -r requirements.txt
python cf_xray_benchmark.py
```

---

## Run modes

| Mode | CLI | Meaning |
|------|-----|---------|
| IP scanner · all configs (**default**) | `mode=ip_all` | Every config × every CF IP |
| IP scanner · selected config | `mode=ip_one` + `config_index=N` | One config × all CF IPs |
| Config benchmark only | `mode=config_only` | Original server address; ignore CF IP list |
| Your internet only | `mode=baseline_only` | Direct line test only (no proxy) |
| CF IP direct test | `mode=cf_direct` | TCP/HTTP probe to CF IPs (no share-link / Xray) |

Examples:

```bash
python cf_xray_benchmark.py mode=ip_all workers=1
python cf_xray_benchmark.py mode=ip_one config_index=0 max_ips=20
python cf_xray_benchmark.py mode=config_only
python cf_xray_benchmark.py mode=baseline_only
python cf_xray_benchmark.py mode=cf_direct
```

In the GUI, pick the mode from **Run mode**. For “selected config”, use the **Select config** dropdown.

---

## Project layout

```text
cf-xray-benchmark/
  cf_xray_benchmark.py   # main CLI
  debug_one.py           # single-config debug (no IP swap)
  gui.py / gui_app.py    # CustomTkinter GUI
  gui.bat
  config.json            # all toggles
  cfip.txt               # IPs / CIDRs / domains
  links.txt              # share-links
  requirements.txt
  setup.bat / setup.sh
  run.bat / run.sh
  README.md / README_FA.md
  fonts/                 # optional Vazirmatn-Regular.ttf
  temp/ results/ logs/   # created at runtime
```

---

## Input files

### `links.txt`

```text
vless://uuid@host:443?security=tls&type=ws&path=/&sni=example.com#MyConfig
# comments ok
```

Supported: `vless://` · `vmess://` · `trojan://`

### `cfip.txt`

```text
# scanner style
1181 - 0 - 172.66.170.97

# plain IP
172.66.45.96

# CIDR (expanded; large nets capped at 4096 hosts)
172.66.170.0/24

# domain (DNS A records)
cdn.example.com
```

---

## How a proxied test works

1. Build a temporary Xray config (server address replaced with the CF IP, except config-only mode)
2. Start local SOCKS on a free high port
3. **Quick probe** — if unreachable or ping **> `filter.max_latency_ms`** → `SKIP`
4. Full latency / download / upload (if enabled)
5. Relay pings (if enabled)
6. Score 0–10 and print a live result block

Results stream to the terminal/GUI log. The GUI **Top 5** panel updates during the run.

---

## Configuration (`config.json`)

Keys starting with `_` are comments only.

| Section | Purpose |
|---------|---------|
| `mode` | `ip_all` \| `ip_one` \| `config_only` \| `baseline_only` \| `cf_direct` |
| `config_index` | 0-based index into `links.txt` when `mode=ip_one` |
| `workers` | Parallel tests (start with `1` on Windows) |
| `max_ips` | Cap IPs (`0` = all) |
| `report_name` | Excel/log filename prefix |
| `clear_temp` | `true` / `false` / `null` (ask) |
| `display.*` | Progress, live results, log file |
| `baseline.enabled` | Direct internet test |
| `filter.*` | Quick probe, max latency ms, probe timeout |
| `tests.latency/download/upload` | Enable + samples / bytes / rounds |
| `relay.*` | Master switch + per-site on/off |
| `scoring.*` | Web / Instagram / Gaming + Overall weights |
| `ranking.top_n` | Rows in Top tables |
| `timeouts.*` | HTTP and Xray startup waits |
| `paths.*` | Filenames and folders |
| `excel.enabled` | Write `results/*.xlsx` |

CLI arguments **override** `config.json` when provided (`workers=`, `max_ips=`, `mode=`, `config_index=`, `clear_temp=`, `report=`, `custom`).

---

## GUI

```bat
gui.bat
```

| Tab | Content |
|-----|---------|
| **Run** | Files, run mode, quick options, Start/Stop, Top 5, live log |
| **Settings** | All options with short descriptions |
| **Advanced** | Raw `config.json` editor |
| **Help** | Full guide (FA/EN) |

- **Language:** FA / EN (Persian uses **Vazirmatn** + RTL when the font is available)
- **Edit** on CF IP / Links opens an in-app text editor
- **Top 5:** left-click copies IP; right-click copies IP / IP+ping / full line
- Place `fonts/Vazirmatn-Regular.ttf` if auto-download fails ([Vazirmatn](https://github.com/rastikerdar/vazirmatn))

---

## Debug one config

```bash
python debug_one.py
python debug_one.py "vless://..."
```

Windows leftover processes:

```powershell
Get-Process xray -ErrorAction SilentlyContinue | Stop-Process -Force
```

---

## Output

| Path | Content |
|------|---------|
| `results/*.xlsx` | Full ranking workbook |
| `results/latest_top.json` | Top list for the GUI |
| `logs/*.log` | Live run log |
| `temp/` | Per-test JSON (`FAILED_*.json` on errors) |

**Scores:** 9–10 excellent · 7–8 good · 5–6 average · 3–4 weak · 0–2 poor

---

## Requirements

- Python **3.9+**
- `requests[socks]`, `openpyxl`, `colorama`, `customtkinter`
- `xray` / `xray.exe` (auto-downloaded if missing)

---

## Tips

1. Start with `workers=1` on Windows; raise only when stable.
2. Allowlist `python.exe` and `xray.exe` in antivirus.
3. Tune `filter.max_latency_ms` (e.g. 1500–2000) to skip bad IPs quickly.
4. Use `max_ips` while experimenting.
5. Keep `clear_temp=false` when inspecting failures.

---

## Credit

Benchmark approach inspired by [ExtremeDot/xray-config-benchmark](https://github.com/ExtremeDot/xray-config-benchmark).  
Core proxy: [XTLS/Xray-core](https://github.com/XTLS/Xray-core).
