#!/bin/bash
# Weekly report runner - executed by cron
# Timezone: Europe/Rome (Milan)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${SCRIPT_DIR}/reports/cron.log"

# Set timezone to Milan
export TZ="Europe/Rome"

# Activate virtual environment
source "${SCRIPT_DIR}/venv/bin/activate"

# Load environment variables
if [ -f "${SCRIPT_DIR}/.env" ]; then
    export $(grep -v '^#' "${SCRIPT_DIR}/.env" | xargs)
fi

# Run the report
echo "$(date): Starting weekly competitor report" >> "$LOG_FILE"
cd "$SCRIPT_DIR"
research-assistant weekly-report -d "${SCRIPT_DIR}/reports" 2>&1 | tee -a "$LOG_FILE"
echo "$(date): Report complete" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
