#!/bin/bash
# SpendWise one-click launcher: setup -> (optional) real evaluation -> app.
cd "$(dirname "$0")" || exit 1
clear
echo "=================  SpendWise  ================="

if [ ! -d .venv ]; then
  echo "Creating Python environment (first time only)..."
  python3 -m venv .venv || exit 1
fi
source .venv/bin/activate
pip install -q -r requirements.txt

echo
echo "Which language model should SpendWise use?"
echo "  1) Google Gemini   (key starts with AQ.  - aistudio.google.com/apikey)"
echo "  2) Groq            (key starts with gsk_ - console.groq.com/keys)"
echo "  3) Offline demo    (no internet, no key - always works)"
read -r -p "Type 1, 2 or 3 and press Enter: " CHOICE

case "$CHOICE" in
  1) BACKEND=gemini;            VAR=GEMINI_API_KEY ;;
  2) BACKEND=openai-compatible; VAR=OPENAI_API_KEY
     export OPENAI_BASE_URL="https://api.groq.com/openai/v1" ;;
  *) BACKEND=offline-simulator; VAR="" ;;
esac

if [ -n "$VAR" ] && [ -z "${!VAR}" ]; then
  echo
  echo "Paste your API key and press Enter (nothing shows while you paste - that's normal):"
  read -r -s KEY
  export "$VAR=$KEY"
  echo "Key received (${#KEY} characters)."
fi

if [ "$BACKEND" != "offline-simulator" ]; then
  echo
  echo "=== Step 1/2: running the prompt evaluation with $BACKEND (a few minutes) ==="
  python evaluate.py --backend "$BACKEND" 2>&1 | tee results/evaluation_log.txt
  if [ "${PIPESTATUS[0]}" -eq 0 ]; then
    echo; echo ">>> Evaluation finished. Open 'Prompt Lab' in the app to see the real results."
  else
    echo; echo ">>> Evaluation did not finish (see above). Finished calls are cached - run this again to resume."
  fi
fi

echo
echo "=== Step 2/2: starting the SpendWise FastAPI backend & React frontend ==="
python -m uvicorn api:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
trap "kill $BACKEND_PID 2>/dev/null" EXIT

cd frontend
if [ ! -d node_modules ]; then
  npm install
fi
npm run dev -- --port 3000 --host 0.0.0.0
