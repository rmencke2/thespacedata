#!/bin/bash
# Setup script for weekly competitor intelligence reports
# Runs every Tuesday at 8:00 AM Milan time (Europe/Rome timezone)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="${SCRIPT_DIR}/venv"
REPORTS_DIR="${SCRIPT_DIR}/reports"

echo "=========================================="
echo "Webnode Competitor Intelligence - Cron Setup"
echo "=========================================="
echo ""
echo "Project directory: ${SCRIPT_DIR}"
echo "Virtual environment: ${VENV_PATH}"
echo "Reports directory: ${REPORTS_DIR}"
echo ""

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_PATH"
fi

# Activate and install
echo "Installing dependencies..."
source "${VENV_PATH}/bin/activate"
pip install -e "${SCRIPT_DIR}" --quiet

# Create reports directory
mkdir -p "$REPORTS_DIR"

# Check for .env file
if [ ! -f "${SCRIPT_DIR}/.env" ]; then
    echo ""
    echo "WARNING: No .env file found!"
    echo "Copy .env.example to .env and configure your API keys:"
    echo "  cp ${SCRIPT_DIR}/.env.example ${SCRIPT_DIR}/.env"
    echo ""
fi

# Create the cron wrapper script
CRON_SCRIPT="${SCRIPT_DIR}/run-weekly-report.sh"
cat > "$CRON_SCRIPT" << 'CRONEOF'
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
CRONEOF

chmod +x "$CRON_SCRIPT"
echo "Created cron wrapper script: ${CRON_SCRIPT}"

# Generate cron entry
# Tuesday = 2, 8:00 AM Milan time
# Milan is UTC+1 (winter) or UTC+2 (summer/DST)
# We'll use the system's timezone handling
CRON_ENTRY="0 8 * * 2 TZ=Europe/Rome ${CRON_SCRIPT}"

echo ""
echo "=========================================="
echo "Cron Setup Instructions"
echo "=========================================="
echo ""
echo "Run this command to edit your crontab:"
echo "  crontab -e"
echo ""
echo "Add this line to run every Tuesday at 8:00 AM Milan time:"
echo ""
echo "  ${CRON_ENTRY}"
echo ""
echo "Or run this command to add it automatically:"
echo "  (crontab -l 2>/dev/null; echo '${CRON_ENTRY}') | crontab -"
echo ""
echo "=========================================="
echo "Quick Test"
echo "=========================================="
echo ""
echo "Test the report generation manually:"
echo "  source ${VENV_PATH}/bin/activate"
echo "  research-assistant weekly-report --no-email"
echo ""
echo "Test with email:"
echo "  research-assistant weekly-report"
echo ""
