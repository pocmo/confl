#!/usr/bin/env bash
# Ralph Loop Agent - iteratively runs an agent until work is complete
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RALPH_DIR="$PROJECT_ROOT/.ralph"
SCRIPT_LOG="$RALPH_DIR/script.log"
AGENT_LOG="$RALPH_DIR/handoff.log"
ARCHIVE_DIR="$RALPH_DIR/archive"
PROMPT_FILE="$RALPH_DIR/prompt.md"
QUESTIONS_FILE="$RALPH_DIR/questions.md"
COPILOT="/opt/homebrew/bin/copilot"

# Defaults
MAX_ITERATIONS=10
ONCE=false

# Log rotation settings
LOG_MAX_LINES=200    # Rotate when log exceeds this many lines
LOG_KEEP_LINES=100   # Keep this many recent lines after rotation

# Rotate handoff log if it gets too long
rotate_handoff_log() {
    if [[ ! -f "$AGENT_LOG" ]]; then
        return
    fi
    
    local line_count
    line_count=$(wc -l < "$AGENT_LOG")
    
    if [[ $line_count -gt $LOG_MAX_LINES ]]; then
        mkdir -p "$ARCHIVE_DIR"
        local timestamp
        timestamp=$(date '+%Y%m%d-%H%M%S')
        local archive_file="$ARCHIVE_DIR/handoff-$timestamp.log"
        
        # Archive the full log
        cp "$AGENT_LOG" "$archive_file"
        
        # Keep only the most recent lines
        tail -n "$LOG_KEEP_LINES" "$AGENT_LOG" > "$AGENT_LOG.tmp"
        
        # Add a note about the rotation
        {
            echo "--- [Log rotated at $(date '+%Y-%m-%d %H:%M:%S')] ---"
            echo "--- Previous entries archived to: archive/$(basename "$archive_file") ---"
            echo ""
            cat "$AGENT_LOG.tmp"
        } > "$AGENT_LOG"
        rm "$AGENT_LOG.tmp"
        
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Rotated handoff.log (was $line_count lines, kept $LOG_KEEP_LINES)" >> "$SCRIPT_LOG"
        echo "📜 Rotated handoff.log → archive/$(basename "$archive_file")"
    fi
}

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Ralph Loop Agent - runs an autonomous coding agent in a loop until work is complete.

OPTIONS:
    --once              Run only one iteration
    --max-iterations N  Maximum number of iterations (default: $MAX_ITERATIONS)
    --help              Show this help message

State is stored in .ralph/
  - prompt.md: Instructions for the agent
  - handoff.log: Notes from agent to agent (append only, auto-rotated)
  - questions.md: Questions for the user
  - archive/: Rotated handoff logs
EOF
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --once)
            ONCE=true
            MAX_ITERATIONS=1
            shift
            ;;
        --max-iterations)
            MAX_ITERATIONS="$2"
            shift 2
            ;;
        --help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Ensure .ralph directory and prompt exist
mkdir -p "$RALPH_DIR"
if [[ ! -f "$PROMPT_FILE" ]]; then
    echo "Error: $PROMPT_FILE not found. Create it with instructions for the agent."
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Ralph loop starting (max iterations: $MAX_ITERATIONS) ===" >> "$SCRIPT_LOG"

iteration=0
while [[ $iteration -lt $MAX_ITERATIONS ]]; do
    iteration=$((iteration + 1))
    iter_start=$(date +%s)
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] --- Iteration $iteration started ---" >> "$SCRIPT_LOG"
    
    # Rotate handoff log if needed
    rotate_handoff_log
    
    # Print visible iteration marker
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  🔄 RALPH ITERATION $iteration of $MAX_ITERATIONS"
    echo "════════════════════════════════════════════════════════════════"
    echo ""

    # Build context for the agent
    prompt_content=$(cat "$PROMPT_FILE")
    handoff_notes=$(tail -50 "$AGENT_LOG" 2>/dev/null || echo "No previous notes")
    pending_questions=""
    if [[ -f "$QUESTIONS_FILE" ]]; then
        pending_questions=$(cat "$QUESTIONS_FILE")
    fi

    # Construct the agent prompt
    agent_prompt=$(cat <<PROMPT
You are Ralph, an autonomous coding agent working on the confl project.

## Your Instructions
$prompt_content

## Handoff Notes from Previous Iterations
$handoff_notes

## Pending Questions for User
$pending_questions

## Project Context
- Working directory: $PROJECT_ROOT
- Handoff log (APPEND your notes here): $AGENT_LOG
- Questions file (for user): $QUESTIONS_FILE
- Run tests: uv run pytest
- Run CLI: uv run confl <command>
- Ticket system: tk (run \`tk help\` for commands)
PROMPT
)

    # Run the agent (output streams directly to terminal)
    "$COPILOT" -p "$agent_prompt" --allow-all-tools || true

    # Log iteration duration
    iter_end=$(date +%s)
    iter_duration=$((iter_end - iter_start))
    iter_mins=$((iter_duration / 60))
    iter_secs=$((iter_duration % 60))
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] --- Iteration $iteration finished (${iter_mins}m ${iter_secs}s) ---" >> "$SCRIPT_LOG"

    # Push changes to remote
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pushing changes to remote..." >> "$SCRIPT_LOG"
    if git push 2>&1 | tee -a "$SCRIPT_LOG"; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Git push successful" >> "$SCRIPT_LOG"
        echo "✅ Pushed changes to remote"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Git push failed or nothing to push" >> "$SCRIPT_LOG"
        echo "⚠️  Git push failed or nothing to push"
    fi

    # Check for completion signal in agent's handoff log
    if [[ -f "$AGENT_LOG" ]] && tail -5 "$AGENT_LOG" | grep -q "COMPLETE"; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Agent signaled COMPLETE. Exiting loop." >> "$SCRIPT_LOG"
        echo ""
        echo "✅ Agent signaled all work is complete."
        break
    fi

    # Check if we should continue
    if [[ "$ONCE" == "true" ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Single iteration mode (--once), exiting." >> "$SCRIPT_LOG"
        echo ""
        echo "⏸️  Single iteration mode (--once), stopping."
        break
    fi

    # Brief pause between iterations
    echo ""
    echo "⏳ Pausing 2 seconds before next iteration..."
    sleep 2
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Ralph loop finished after $iteration iteration(s) ===" >> "$SCRIPT_LOG"
echo ""
echo "🏁 Ralph loop finished after $iteration iteration(s)."
