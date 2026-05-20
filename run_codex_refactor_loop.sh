#!/usr/bin/env bash
set -u

PROJECT_DIR="$(pwd)"
LOG_DIR="$PROJECT_DIR/agent_logs"
STOP_FILE="$PROJECT_DIR/STOP_AGENT"
TASK_FILE="${TASK_FILE:-AGENT_TASK.md}"
MAX_CYCLES="${MAX_CYCLES:-96}"
SLEEP_SECONDS="${SLEEP_SECONDS:-1800}"
PYTHON_BIN="${PYTHON_BIN:-}"
CODEX_SANDBOX="${CODEX_SANDBOX:-workspace-write}"
AUTO_COMMIT="${AUTO_COMMIT:-1}"
AUTO_PUSH="${AUTO_PUSH:-1}"
REMOTE_NAME="${REMOTE_NAME:-origin}"
BRANCH_NAME="${BRANCH_NAME:-$(git branch --show-current 2>/dev/null || echo main)}"
RUN_PYTEST="${RUN_PYTEST:-1}"
STREAMLIT_APP_URL="${STREAMLIT_APP_URL:-}"
COMMIT_PREFIX="${COMMIT_PREFIX:-UX/UI agent cycle}"
PYTHONPYCACHEPREFIX="${PYTHONPYCACHEPREFIX:-/private/tmp/luxstats_pycache}"

finish() {
  local exit_code=$?
  echo ""
  echo "===== Refactor loop stopped: $(date) =====" | tee -a "$LOG_DIR/loop.log"
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Latest commit: $(git log -1 --oneline)" | tee -a "$LOG_DIR/loop.log"
    if [ -n "$(git status --porcelain)" ]; then
      echo "Uncommitted changes remain:" | tee -a "$LOG_DIR/loop.log"
      git status --short | tee -a "$LOG_DIR/loop.log"
    else
      echo "Working tree clean." | tee -a "$LOG_DIR/loop.log"
    fi
  fi
  if [ -n "$STREAMLIT_APP_URL" ]; then
    echo "Streamlit app: $STREAMLIT_APP_URL" | tee -a "$LOG_DIR/loop.log"
  else
    echo "Set STREAMLIT_APP_URL=https://your-app.streamlit.app to print the direct app link here." | tee -a "$LOG_DIR/loop.log"
  fi
  exit "$exit_code"
}

trap finish EXIT
trap 'echo "Stop requested. Finishing current shell step and exiting."; exit 130' INT TERM

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
echo "Auto commit: $AUTO_COMMIT"
echo "Auto push: $AUTO_PUSH ($REMOTE_NAME $BRANCH_NAME)"
if [ -n "$STREAMLIT_APP_URL" ]; then
  echo "Streamlit app: $STREAMLIT_APP_URL"
fi

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
    --sandbox "$CODEX_SANDBOX" \
    --output-last-message "$LOG_DIR/codex_cycle_${i}.md" \
    "$(cat "$TASK_FILE")" \
    2>&1 | tee "$LOG_DIR/codex_cycle_${i}.log"

  EXIT_CODE=${PIPESTATUS[0]}

  echo "Codex exit code: $EXIT_CODE" | tee -a "$LOG_DIR/loop.log"

  echo "Running validation..." | tee -a "$LOG_DIR/loop.log"
  {
    echo "Python compile check"
    PYTHONPYCACHEPREFIX="$PYTHONPYCACHEPREFIX" \
      "$PYTHON_BIN" -m py_compile app.py pages/*.py src/*.py tests/*.py
    if [ "$RUN_PYTEST" = "1" ]; then
      echo ""
      echo "Pytest"
      PYTHONPYCACHEPREFIX="$PYTHONPYCACHEPREFIX" \
        "$PYTHON_BIN" -m pytest -q
    fi
  } 2>&1 | tee "$LOG_DIR/validation_cycle_${i}.log"
  VALIDATION_CODE=${PIPESTATUS[0]}

  if [ "$VALIDATION_CODE" -ne 0 ]; then
    echo "Validation failed. Asking Codex to fix only the validation errors." | tee -a "$LOG_DIR/loop.log"

    codex exec \
      --sandbox "$CODEX_SANDBOX" \
      --output-last-message "$LOG_DIR/codex_fix_cycle_${i}.md" \
      "The previous validation failed. Read agent_logs/validation_cycle_${i}.log and fix only the errors needed to make validation pass. Do not refactor unrelated files." \
      2>&1 | tee "$LOG_DIR/codex_fix_cycle_${i}.log"

    {
      echo "Python compile check"
      PYTHONPYCACHEPREFIX="$PYTHONPYCACHEPREFIX" \
        "$PYTHON_BIN" -m py_compile app.py pages/*.py src/*.py tests/*.py
      if [ "$RUN_PYTEST" = "1" ]; then
        echo ""
        echo "Pytest"
        PYTHONPYCACHEPREFIX="$PYTHONPYCACHEPREFIX" \
          "$PYTHON_BIN" -m pytest -q
      fi
    } 2>&1 | tee "$LOG_DIR/validation_after_fix_cycle_${i}.log"
    VALIDATION_CODE=${PIPESTATUS[0]}
  fi

  if [ "$VALIDATION_CODE" -eq 0 ]; then
    if [ -n "$(git status --porcelain)" ]; then
      if [ "$AUTO_COMMIT" = "1" ]; then
        git add -A
        git commit -m "$COMMIT_PREFIX $i" 2>&1 | tee -a "$LOG_DIR/loop.log"
        if [ "$AUTO_PUSH" = "1" ]; then
          git push "$REMOTE_NAME" "$BRANCH_NAME" 2>&1 | tee -a "$LOG_DIR/loop.log"
          if [ -n "$STREAMLIT_APP_URL" ]; then
            echo "Streamlit Cloud should redeploy from $REMOTE_NAME/$BRANCH_NAME. Open: $STREAMLIT_APP_URL" | tee -a "$LOG_DIR/loop.log"
          else
            echo "Pushed to $REMOTE_NAME/$BRANCH_NAME. Streamlit Cloud should redeploy if this branch is connected." | tee -a "$LOG_DIR/loop.log"
          fi
        fi
      else
        echo "AUTO_COMMIT=0, leaving changes uncommitted." | tee -a "$LOG_DIR/loop.log"
      fi
    else
      echo "No changes to commit." | tee -a "$LOG_DIR/loop.log"
    fi
  else
    echo "Validation still failed. Leaving changes uncommitted for review." | tee -a "$LOG_DIR/loop.log"
    git status --short | tee -a "$LOG_DIR/loop.log"
    exit 1
  fi

  echo "===== Cycle $i finished: $(date) =====" | tee -a "$LOG_DIR/loop.log"
  if [ -f "$STOP_FILE" ]; then
    echo "STOP_AGENT found after cycle. Exiting before sleep." | tee -a "$LOG_DIR/loop.log"
    exit 0
  fi
  echo "Sleeping for $SLEEP_SECONDS seconds... create STOP_AGENT to stop before the next cycle."
  sleep "$SLEEP_SECONDS"
done

echo "Reached MAX_CYCLES=$MAX_CYCLES. Exiting."
