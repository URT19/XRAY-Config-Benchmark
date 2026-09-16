# -*- coding: utf-8 -*-
"""
Debug / Single Config Test
==========================
Tests ONE config link as-is (no CF IP swap).
Verbose output so you can see exactly where it fails.

Usage:
  1. Put your working link in links.txt  (first non-comment line)
  2. python debug_one.py
  3. Or: python debug_one.py "vless://uuid@host:443?..."

Dependencies:
  pip install requests[socks] colorama
"""

from __future__ import annotations

import os
import sys
import json
import time
import base64
import statistics
import subprocess
import tempfile
import zipfile
import platform
import urllib.parse
from pathlib import Path
from urllib.request import urlretrieve

import requests

try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init(autoreset=True)
except ImportError:
    class _D:
        def __getattr__(self, n): return ""
    Fore = Style = _D()  # type: ignore

SOCKS_PORT = 10999
TIMEOUT = 15
XRAY_STARTUP_WAIT = 3.0

XRAY_WINDOWS_URL = "https://github.com/XTLS/Xray-core/releases/download/v26.3.27/Xray-windows-64.zip"
XRAY_LINUX_URL = "https://github.com/XTLS/Xray-core/releases/download/v26.3.27/Xray-linux-64.zip"


def c(t, color=""): return f"{color}{t}{Style.RESET_ALL}"
def info(m): print(c("[INFO] ", Fore.CYAN) + m)
def ok(m): print(c("[ OK ] ", Fore.GREEN) + m)
def warn(m): print(c("[WARN] ", Fore.YELLOW) + m)
def err(m): print(c("[ERR ] ", Fore.RED) + m)
def step(n, m): print(c(f"\n=== STEP {n}: {m} ===", Fore.MAGENTA + Style.BRIGHT))


def is_windows():
    return platform.system().lower() == "windows"


def ensure_xray() -> str:
    name = "xray.exe" if is_windows() else "xray"
    path = Path(name)
    if path.exists():
        ok(f"Found {name}")
        return str(path.resolve())

    warn(f"{name} not found, downloading...")
    url = XRAY_WINDOWS_URL if is_windows() else XRAY_LINUX_URL
    zip_path = Path("xray_download.zip")
    try:
        urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, "r") as zf:
            for member in zf.namelist():
                if member.lower().endswith(name) or member.lower().endswith("xray"):
                    zf.extract(member, path=".")
                    extracted = Path(member)
                    if extracted.name != name:
                        extracted.replace(path)
                    break
            else:
                zf.extractall(".")
                for p in Path(".").rglob("*"):
                    if p.is_file() and p.name.lower() in (name, "xray"):
                        if p != path:
                            p.replace(path)
                        break
        if zip_path.exists():
            zip_path.unlink(missing_ok=True)
        if not path.exists():
            raise FileNotFoundError("xray not found after extract")
        if not is_windows():
            os.chmod(path, 0o755)
        ok(f"{name} ready")
        return str(path.resolve())
    except Exception as e:
        err(f"xray download failed: {e}")
        sys.exit(1)


# ---- parsers (same as main, simplified) ----

def parse_vless(link: str):
    link = link.strip()
    if not link.startswith("vless://"):
        return None
    rest = link[8:]
    remark = "vless"
    if "#" in rest:
        rest, remark = rest.rsplit("#", 1)
        remark = urllib.parse.unquote(remark)
    if "?" in rest:
        main, query = rest.split("?", 1)
        params = dict(urllib.parse.parse_qsl(query))
    else:
        main, params = rest, {}
    uuid, server_part = main.split("@", 1)
    address, port = server_part.rsplit(":", 1)
    port = int(port)
    network = params.get("type", "tcp")
    security = params.get("security", "none")
    sni = params.get("sni") or params.get("host") or address
    fp = params.get("fp", "")
    alpn = params.get("alpn", "")
    flow = params.get("flow", "")
    path = params.get("path", "")
    host = params.get("host", "")
    service_name = params.get("serviceName", "")
    insecure = params.get("allowInsecure", params.get("insecure", "0")) == "1"

    stream = {"network": network, "security": security}
    if security in ("tls", "reality"):
        tls = {"serverName": sni, "allowInsecure": insecure}
        if fp:
            tls["fingerprint"] = fp
        if alpn:
            tls["alpn"] = alpn.split(",")
        if security == "reality":
            tls["publicKey"] = params.get("pbk", "")
            tls["shortId"] = params.get("sid", "")
            tls["spiderX"] = params.get("spx", "")
            stream["realitySettings"] = tls
        else:
            stream["tlsSettings"] = tls
    if network == "ws":
        stream["wsSettings"] = {"path": path or "/", "headers": {"Host": host or sni}}
    elif network == "grpc":
        stream["grpcSettings"] = {"serviceName": service_name, "multiMode": params.get("mode", "gun") == "multi"}
    elif network == "httpupgrade":
        stream["httpupgradeSettings"] = {"path": path or "/", "host": host or sni}
    elif network == "xhttp":
        stream["xhttpSettings"] = {"path": path or "/", "host": host or sni}

    outbound = {
        "tag": "proxy",
        "protocol": "vless",
        "settings": {
            "vnext": [{
                "address": address, "port": port,
                "users": [{"id": uuid, "encryption": params.get("encryption", "none"), "flow": flow}]
            }]
        },
        "streamSettings": stream
    }
    return {"remark": remark, "outbound": outbound, "address": address, "port": port}


def parse_trojan(link: str):
    link = link.strip()
    if not link.startswith("trojan://"):
        return None
    rest = link[9:]
    remark = "trojan"
    if "#" in rest:
        rest, remark = rest.rsplit("#", 1)
        remark = urllib.parse.unquote(remark)
    if "?" in rest:
        main, query = rest.split("?", 1)
        params = dict(urllib.parse.parse_qsl(query))
    else:
        main, params = rest, {}
    password, server_part = main.split("@", 1)
    address, port = server_part.rsplit(":", 1)
    port = int(port)
    sni = params.get("sni") or params.get("peer") or address
    network = params.get("type", "tcp")
    fp = params.get("fp", "")
    path = params.get("path", "")
    host = params.get("host", "")
    insecure = params.get("allowInsecure", "0") == "1"

    stream = {
        "network": network, "security": "tls",
        "tlsSettings": {"serverName": sni, "allowInsecure": insecure}
    }
    if fp:
        stream["tlsSettings"]["fingerprint"] = fp
    if network == "ws":
        stream["wsSettings"] = {"path": path or "/", "headers": {"Host": host or sni}}

    outbound = {
        "tag": "proxy", "protocol": "trojan",
        "settings": {"servers": [{"address": address, "port": port, "password": password}]},
        "streamSettings": stream
    }
    return {"remark": remark, "outbound": outbound, "address": address, "port": port}


def parse_vmess(link: str):
    link = link.strip()
    if not link.startswith("vmess://"):
        return None
    b64 = link[8:] + "=" * (-len(link[8:]) % 4)
    data = json.loads(base64.b64decode(b64).decode("utf-8"))
    address = data.get("add")
    port = int(data.get("port", 443))
    uuid = data.get("id")
    network = data.get("net", "tcp")
    tls = data.get("tls", "")
    sni = data.get("sni") or data.get("host") or address
    path = data.get("path", "")
    host = data.get("host", "")
    remark = data.get("ps", "vmess")

    stream = {"network": network}
    if tls in ("tls", "reality"):
        stream["security"] = tls
        stream["tlsSettings" if tls == "tls" else "realitySettings"] = {
            "serverName": sni, "allowInsecure": False
        }
    else:
        stream["security"] = "none"
    if network == "ws":
        stream["wsSettings"] = {"path": path or "/", "headers": {"Host": host or sni}}

    outbound = {
        "tag": "proxy", "protocol": "vmess",
        "settings": {
            "vnext": [{
                "address": address, "port": port,
                "users": [{"id": uuid, "alterId": int(data.get("aid", 0)), "security": data.get("scy", "auto")}]
            }]
        },
        "streamSettings": stream
    }
    return {"remark": remark, "outbound": outbound, "address": address, "port": port}


def parse_link(link: str):
    if link.startswith("vless://"):
        return parse_vless(link)
    if link.startswith("trojan://"):
        return parse_trojan(link)
    if link.startswith("vmess://"):
        return parse_vmess(link)
    return None


def make_config(parsed, socks_port):
    return {
        "log": {"loglevel": "warning"},
        "inbounds": [{
            "tag": "socks",
            "port": socks_port,
            "listen": "127.0.0.1",
            "protocol": "mixed",
            "settings": {"auth": "noauth", "udp": True}
        }],
        "outbounds": [
            parsed["outbound"],
            {"tag": "direct", "protocol": "freedom"}
        ],
        "routing": {
            "domainStrategy": "AsIs",
            "rules": [{"type": "field", "outboundTag": "proxy", "network": "tcp,udp"}]
        }
    }


def main():
    print(c("\n" + "=" * 60, Fore.MAGENTA))
    print(c("  DEBUG ONE CONFIG  (no IP swap)", Fore.MAGENTA + Style.BRIGHT))
    print(c("=" * 60 + "\n", Fore.MAGENTA))

    # Get link
    link = None
    if len(sys.argv) > 1 and "://" in sys.argv[1]:
        link = sys.argv[1].strip()
        info("Using link from command line")
    else:
        p = Path("links.txt")
        if p.exists():
            for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "://" in line:
                    link = line
                    break
        if not link:
            err("No link found. Put a working link in links.txt or pass it as argument.")
            err('  Example: python debug_one.py "vless://uuid@host:443?..."')
            sys.exit(1)
        info("Using first link from links.txt")

    print(c(f"\nLink (truncated): {link[:80]}...", Fore.WHITE))

    # Step 1: parse
    step(1, "Parse link")
    try:
        parsed = parse_link(link)
    except Exception as e:
        err(f"Parse exception: {e}")
        sys.exit(1)
    if not parsed:
        err("Parse failed (unsupported or invalid link)")
        sys.exit(1)
    ok(f"Remark   : {parsed['remark']}")
    ok(f"Address  : {parsed['address']}")
    ok(f"Port     : {parsed['port']}")
    ok(f"Protocol : {parsed['outbound']['protocol']}")
    net = parsed["outbound"].get("streamSettings", {}).get("network", "?")
    sec = parsed["outbound"].get("streamSettings", {}).get("security", "?")
    ok(f"Network  : {net}  Security: {sec}")

    # Step 2: xray binary
    step(2, "Locate / download xray")
    xray_path = ensure_xray()

    # Step 3: write config
    step(3, "Write temp config + start xray")
    config = make_config(parsed, SOCKS_PORT)
    conf_path = None
    proc = None
    try:
        fd, conf_path = tempfile.mkstemp(suffix=".json", prefix="debug_")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        info(f"Config file: {conf_path}")

        # show outbound address for confirmation
        out = config["outbounds"][0]
        if out["protocol"] in ("vless", "vmess"):
            addr = out["settings"]["vnext"][0]["address"]
            port = out["settings"]["vnext"][0]["port"]
        else:
            addr = out["settings"]["servers"][0]["address"]
            port = out["settings"]["servers"][0]["port"]
        info(f"Outbound target: {addr}:{port}")

        flags = 0
        if is_windows():
            flags = subprocess.CREATE_NO_WINDOW  # type: ignore

        proc = subprocess.Popen(
            [xray_path, "run", "-c", conf_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=flags
        )
        info(f"xray PID: {proc.pid}  waiting {XRAY_STARTUP_WAIT}s...")
        time.sleep(XRAY_STARTUP_WAIT)

        if proc.poll() is not None:
            out_b, err_b = proc.communicate(timeout=2)
            err("xray exited immediately!")
            if err_b:
                print(c(err_b.decode(errors="replace")[:800], Fore.RED))
            if out_b:
                print(c(out_b.decode(errors="replace")[:400], Fore.YELLOW))
            sys.exit(1)
        ok("xray is running")
    except Exception as e:
        err(f"Failed to start xray: {e}")
        if proc:
            proc.kill()
        sys.exit(1)

    proxies = {
        "http": f"socks5h://127.0.0.1:{SOCKS_PORT}",
        "https": f"socks5h://127.0.0.1:{SOCKS_PORT}",
    }

    # Step 4: exit IP
    step(4, "Get exit IP via proxy")
    try:
        r = requests.get("https://www.cloudflare.com/cdn-cgi/trace", proxies=proxies, timeout=TIMEOUT)
        if r.status_code == 200:
            trace = {}
            for line in r.text.strip().splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    trace[k] = v
            ok(f"Exit IP : {trace.get('ip', '?')}")
            ok(f"Loc     : {trace.get('loc', '?')}")
            ok(f"Colo    : {trace.get('colo', '?')}")
        else:
            warn(f"trace status={r.status_code}")
            r2 = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=TIMEOUT)
            ok(f"Exit IP (ipify): {r2.json().get('ip', '?')}")
    except Exception as e:
        err(f"Exit IP test FAILED: {type(e).__name__}: {e}")
        err("Proxy is not working. Check config / network / firewall.")
        proc.terminate()
        if conf_path and os.path.exists(conf_path):
            os.unlink(conf_path)
        sys.exit(1)

    # Step 5: latency
    step(5, "Latency test (5 samples)")
    times = []
    for i in range(5):
        t0 = time.perf_counter()
        try:
            r = requests.get("https://www.cloudflare.com/cdn-cgi/trace", proxies=proxies, timeout=TIMEOUT)
            ms = (time.perf_counter() - t0) * 1000
            if r.status_code == 200:
                times.append(ms)
                ok(f"  sample {i+1}: {ms:.0f} ms")
            else:
                warn(f"  sample {i+1}: status {r.status_code}")
        except Exception as e:
            err(f"  sample {i+1}: {type(e).__name__}")
        time.sleep(0.1)
    if times:
        ok(f"Latency avg={statistics.mean(times):.0f} ms  min={min(times):.0f}  max={max(times):.0f}")
    else:
        err("All latency samples failed")

    # Step 6: small download
    step(6, "Download test (250 KB)")
    try:
        t0 = time.perf_counter()
        r = requests.get(
            "https://speed.cloudflare.com/__down?bytes=250000",
            proxies=proxies, timeout=TIMEOUT
        )
        elapsed = time.perf_counter() - t0
        if r.status_code == 200 and elapsed > 0.05:
            mbps = (250000 * 8) / (elapsed * 1_000_000)
            ok(f"Download: {mbps:.2f} Mbps  ({elapsed:.2f}s)")
        else:
            warn(f"Download status={r.status_code}")
    except Exception as e:
        err(f"Download failed: {type(e).__name__}: {e}")

    # cleanup
    step(7, "Cleanup")
    try:
        proc.terminate()
        proc.wait(timeout=3)
    except Exception:
        proc.kill()
    if conf_path and os.path.exists(conf_path):
        os.unlink(conf_path)
    ok("Done. If all steps above are green, your config works.")
    print()


if __name__ == "__main__":
    main()
