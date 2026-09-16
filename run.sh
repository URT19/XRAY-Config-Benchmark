#!/usr/bin/env bash
cd "$(dirname "$0")"

echo "========================================"
echo " CF Xray IP Benchmark"
echo "========================================"
echo

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERR] python3 not found. Run ./setup.sh first."
  exit 1
fi

# Kill leftover xray if any
pkill -f '[x]ray' 2>/dev/null || true

python3 cf_xray_benchmark.py "$@"
code=$?
echo
if [ "$code" -ne 0 ]; then
  echo "[ERR] Exit code $code"
else
  echo "[OK] Finished."
fi
exit $code
