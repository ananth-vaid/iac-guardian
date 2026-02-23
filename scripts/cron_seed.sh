#!/bin/bash
# Daily cron wrapper for seed_demo_metrics.py
# Runs through Feb 24 2026, then self-removes from crontab.
# Logs to /tmp/iac_guardian_seed.log

DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG="/tmp/iac_guardian_seed.log"
EXPIRY="20260224"

today=$(date +%Y%m%d)
if [ "$today" -gt "$EXPIRY" ]; then
    echo "$(date): Expiry reached ($EXPIRY), removing cron job." >> "$LOG"
    crontab -l 2>/dev/null | grep -v cron_seed.sh | crontab -
    exit 0
fi

echo "$(date): Running IaC Guardian seed (expires $EXPIRY)..." >> "$LOG"

source "$DIR/venv/bin/activate" && \
  source "$DIR/.env" && \
  python3 "$DIR/scripts/seed_demo_metrics.py" >> "$LOG" 2>&1

echo "$(date): Done." >> "$LOG"
