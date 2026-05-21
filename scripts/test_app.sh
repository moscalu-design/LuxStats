#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "==> Compile check"
"$PYTHON_BIN" -m compileall app.py pages src tests scripts

echo "==> Unit and smoke tests"
if "$PYTHON_BIN" -m pytest --version >/dev/null 2>&1; then
  "$PYTHON_BIN" -m pytest "$@"
else
  echo "pytest is not installed for $PYTHON_BIN; skipping pytest. Install requirements with: $PYTHON_BIN -m pip install -r requirements.txt"
fi

echo "==> Streamlit import check"
"$PYTHON_BIN" - <<'PY'
import importlib.util
import sys

if importlib.util.find_spec("streamlit") is None:
    print("streamlit is not installed; skipping Streamlit runtime smoke check.")
    sys.exit(0)

for module in ["app", "src.home", "src.catalog", "src.data.commune_portal", "src.data.communes"]:
    __import__(module)
print("Core Streamlit modules import successfully.")
PY

echo "==> Optional browser tests"
if compgen -G "tests/e2e/test_*.py" >/dev/null; then
  if "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1
import importlib.util
raise SystemExit(0 if importlib.util.find_spec("playwright") else 1)
PY
  then
    "$PYTHON_BIN" -m pytest tests/e2e
  else
    echo "Playwright is not installed; skipping browser e2e tests."
  fi
else
  echo "No e2e tests configured yet."
fi
