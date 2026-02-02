# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Prefer running in a dedicated tmux session for easy inspection
if command -v tmux >/dev/null 2>&1; then
  # Create a detached session called 'autoshutdown' if it doesn't exist
  if tmux has-session -t autoshutdown 2>/dev/null; then
    echo "tmux session 'autoshutdown' already running"
  else
    # Run the venv's python directly (avoids activate setting an absolute VIRTUAL_ENV path)
    tmux new-session -d -s autoshutdown "bash -lc '"$SCRIPT_DIR"/.venv/bin/python autoshutdown.py -v --server minecraft --port 25565'"
    # Verify session started and report failure if it exited immediately
    sleep 1
    if tmux has-session -t autoshutdown 2>/dev/null; then
      echo "Started autoshutdown in tmux session 'autoshutdown'"
    else
      echo "Failed to start autoshutdown in tmux; check logs or run the command manually:" >&2
      echo "  "$SCRIPT_DIR"/.venv/bin/python autoshutdown.py -v --server minecraft --port 25565" >&2
      exit 1
    fi
  fi
else
  # Fallback: run in background using the venv python directly
  "$SCRIPT_DIR"/.venv/bin/python autoshutdown.py -v --server minecraft --port 25565 &
fi
