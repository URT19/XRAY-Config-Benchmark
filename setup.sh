#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "========================================"
echo " CF Xray IP Benchmark - Setup (Linux)"
echo "========================================"
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERR] python3 not found. Install Python 3.9+."
  exit 1
fi

python3 --version
echo
echo "Installing dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo
echo "[OK] Setup complete."
echo
echo "Next:"
echo "  1. Put share-links in links.txt"
echo "  2. Put CF IPs in cfip.txt"
echo "  3. Edit config.json if needed"
echo "  4. Run ./run.sh"
