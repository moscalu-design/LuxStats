#!/usr/bin/env bash
set -u

PROJECT_DIR="$(pwd)"
LOG_DIR="$PROJECT_DIR/agent_logs"
STOP_FILE="$PROJECT_DIR/STOP_AGENT"
TASK_FILE="${TASK_FILE:-AGENT_TASK.md}"
MAX_CYCLES="${MAX_CYCLES:-96}"
SLEEP_SECONDS="${SLEEP_SECONDS:-1800}"
PYTHON_BIN="${PYTHON_BIN:-}"

if [ -z "$PYTHON_BIN" ]; then
  if [ -x "$PROJECT_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
  elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  else
    echo "No Python interpreter found. Set PYTHON_BIN or install python3."
    exit 1
  fi
fi

mkdir -p "$LOG_DIR"

echo "Starting Codex refactor loop in: $PROJECT_DIR"
echo "Create STOP_AGENT in the project root to stop the loop."
echo "Using task file: $TASK_FILE"
echo "Using Python: $PYTHON_BIN"

if [ ! -f "$TASK_FILE" ]; then
  echo "Missing task file: $TASK_FILE"
  echo "Create $TASK_FILE with the instructions for each Codex cycle."
  exit 1
fi

for ((i=1; i<=MAX_CYCLES; i++)); do
  if [ -f "$STOP_FILE" ]; then
    echo "STOP_AGENT found. Exiting."
    exit 0
  fi

  echo ""
  echo "===== Cycle $i started: $(date) =====" | tee -a "$LOG_DIR/loop.log"

  git status --short | tee -a "$LOG_DIR/loop.log"

  codex exec \
    --sandbox workspace-write \
    --output-last-message "$LOG_DIR/codex_cycle_${i}.md" \
    "$(cat "$TASK_FILE")" \
    2>&1 | tee "$LOG_DIR/codex_cycle_${i}.log"

  EXIT_CODE=${PIPESTATUS[0]}

  echo "Codex exit code: $EXIT_CODE" | tee -a "$LOG_DIR/loop.log"

  echo "Running validation..." | tee -a "$LOG_DIR/loop.log"
  PYTHONPYCACHEPREFIX="${PYTHONPYCACHEPREFIX:-/private/tmp/luxstats_pycache}" \
    "$PYTHON_BIN" -m py_compile app.py pages/*.py src/*.py tests/*.py \
    2>&1 | tee "$LOG_DIR/validation_cycle_${i}.log"
  VALIDATION_CODE=${PIPESTATUS[0]}

  if [ "$VALIDATION_CODE" -ne 0 ]; then
    echo "Validation failed. Asking Codex to fix only the validation errors." | tee -a "$LOG_DIR/loop.log"

    codex exec \
      --sandbox workspace-write \
      --output-last-message "$LOG_DIR/codex_fix_cycle_${i}.md" \
      "The previous validation failed. Read agent_logs/validation_cycle_${i}.log and fix only the errors needed to make validation pass. Do not refactor unrelated files." \
      2>&1 | tee "$LOG_DIR/codex_fix_cycle_${i}.log"

    PYTHONPYCACHEPREFIX="${PYTHONPYCACHEPREFIX:-/private/tmp/luxstats_pycache}" \
      "$PYTHON_BIN" -m py_compile app.py pages/*.py src/*.py tests/*.py \
      2>&1 | tee "$LOG_DIR/validation_after_fix_cycle_${i}.log"
    VALIDATION_CODE=${PIPESTATUS[0]}
  fi

  if [ "$VALIDATION_CODE" -eq 0 ]; then
    if [ -n "$(git status --porcelain)" ]; then
      git add .
      git commit -m "Agent refactor cycle $i" 2>&1 | tee -a "$LOG_DIR/loop.log"
    else
      echo "No changes to commit." | tee -a "$LOG_DIR/loop.log"
    fi
  else
    echo "Validation still failed. Leaving changes uncommitted for review." | tee -a "$LOG_DIR/loop.log"
    git status --short | tee -a "$LOG_DIR/loop.log"
    exit 1
  fi

  echo "===== Cycle $i finished: $(date) =====" | tee -a "$LOG_DIR/loop.log"
  echo "Sleeping for $SLEEP_SECONDS seconds..."
  sleep "$SLEEP_SECONDS"
done

echo "Reached MAX_CYCLES=$MAX_CYCLES. Exiting."
