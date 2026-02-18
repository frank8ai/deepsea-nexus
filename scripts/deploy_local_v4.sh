#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${NEXUS_PYTHON_PATH:-python3}"
MODE="${1:---full}"

echo "[deploy] Deep-Sea Nexus local deploy (v4.3)"
echo "[deploy] root=${ROOT_DIR}"
echo "[deploy] python=${PYTHON_BIN}"

cd "${ROOT_DIR}"

if [[ "${MODE}" == "--quick" ]]; then
  echo "[deploy] quick mode: run unit tests only"
  "${PYTHON_BIN}" tests/test_units.py -v
else
  echo "[deploy] full mode: run full test gate"
  "${PYTHON_BIN}" run_tests.py
fi

echo "[deploy] runtime smoke check"
"${PYTHON_BIN}" - <<'PY'
import json
import os
import sys

root = os.getcwd()
parent = os.path.dirname(root)
if parent not in sys.path:
    sys.path.insert(0, parent)

from deepsea_nexus import __version__ as pkg_version
from deepsea_nexus import nexus_health, nexus_init

ok = nexus_init()
if not ok:
    raise SystemExit("nexus_init failed")

health = nexus_health()
if not health.get("available"):
    raise SystemExit("nexus unavailable")
if not health.get("initialized"):
    raise SystemExit("nexus plugin not initialized")

print(json.dumps({
    "available": bool(health.get("available")),
    "initialized": bool(health.get("initialized")),
    "documents": int(health.get("documents", 0)),
    "plugin_version": health.get("version"),
    "package_version": pkg_version,
}, ensure_ascii=False))
PY

echo "[deploy] done"
