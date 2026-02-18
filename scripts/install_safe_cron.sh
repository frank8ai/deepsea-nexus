#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${NEXUS_PYTHON_PATH:-python3}"
MODE="${1:---install}"

BEGIN_MARK="# BEGIN deepsea-nexus-v4.3.1"
END_MARK="# END deepsea-nexus-v4.3.1"

CRON_BLOCK=$(cat <<CRON
${BEGIN_MARK}
# Smart Context report-only digests (safe mode)
0 8 * * * cd ${ROOT_DIR} && ${PYTHON_BIN} scripts/smart_context_digest.py --mode morning >/tmp/deepsea_nexus_digest_morning.log 2>&1
30 11 * * * cd ${ROOT_DIR} && ${PYTHON_BIN} scripts/smart_context_digest.py --mode progress >/tmp/deepsea_nexus_digest_progress_1130.log 2>&1
30 17 * * * cd ${ROOT_DIR} && ${PYTHON_BIN} scripts/smart_context_digest.py --mode progress >/tmp/deepsea_nexus_digest_progress_1730.log 2>&1
0 3 * * * cd ${ROOT_DIR} && ${PYTHON_BIN} scripts/smart_context_digest.py --mode nightly >/tmp/deepsea_nexus_digest_nightly.log 2>&1
10 3 * * * cd ${ROOT_DIR} && ${PYTHON_BIN} scripts/flush_summaries.py >/tmp/deepsea_nexus_flush_summaries.log 2>&1
${END_MARK}
CRON
)

existing="$(crontab -l 2>/dev/null || true)"

cleaned="$(printf '%s\n' "$existing" | awk -v begin="$BEGIN_MARK" -v end="$END_MARK" '
  $0==begin {skip=1; next}
  $0==end {skip=0; next}
  skip==0 {print}
')"

if [[ "$MODE" == "--remove" ]]; then
  printf '%s\n' "$cleaned" | crontab -
  echo "[cron] removed deepsea-nexus-v4.3.1 block"
  exit 0
fi

# install (default)
new_cron="$cleaned"
if [[ -n "$new_cron" ]]; then
  new_cron+=$'\n'
fi
new_cron+="$CRON_BLOCK"

printf '%s\n' "$new_cron" | crontab -
echo "[cron] installed deepsea-nexus-v4.3.1 block"
crontab -l | sed -n '/deepsea-nexus-v4.3.1/,+8p'
