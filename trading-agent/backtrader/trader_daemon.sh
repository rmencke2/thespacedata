#!/bin/bash
#
# Alpaca Crypto Trading Daemon Setup
# Makes the trader run as a background service with auto-restart
#
# This will:
# 1. Run trader in background
# 2. Auto-restart if it crashes
# 3. Auto-start when laptop reboots
# 4. Log everything to file
# 5. Allow easy start/stop/status
#

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TRADER_SCRIPT="$SCRIPT_DIR/alpaca_crypto_paper_trader.py"
LOG_DIR="$SCRIPT_DIR/logs"
PID_FILE="$SCRIPT_DIR/trader.pid"
LOG_FILE="$LOG_DIR/trader_$(date +%Y%m%d).log"

# Create log directory
mkdir -p "$LOG_DIR"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if trader is running
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# Function to start trader
start_trader() {
    echo -e "${GREEN}🚀 Starting Alpaca Crypto Trader...${NC}"
    
    # Check if already running
    if is_running; then
        echo -e "${YELLOW}⚠️  Trader is already running (PID: $(cat $PID_FILE))${NC}"
        return 1
    fi
    
    # Check for API keys
    if [ -z "$ALPACA_API_KEY" ] || [ -z "$ALPACA_SECRET_KEY" ]; then
        echo -e "${RED}❌ Error: Alpaca API keys not set${NC}"
        echo "Please set environment variables:"
        echo "  export ALPACA_API_KEY='your_key'"
        echo "  export ALPACA_SECRET_KEY='your_secret'"
        return 1
    fi
    
    # Start trader in background with auto-restart wrapper
    nohup bash -c "
        while true; do
            echo '========================================' >> '$LOG_FILE'
            echo 'Starting trader at \$(date)' >> '$LOG_FILE'
            echo '========================================' >> '$LOG_FILE'
            
            cd '$SCRIPT_DIR'
            python3 '$TRADER_SCRIPT' <<EOF 2>&1 | tee -a '$LOG_FILE'
2
EOF
            
            EXIT_CODE=\$?
            echo '' >> '$LOG_FILE'
            echo 'Trader stopped at \$(date) with exit code '\$EXIT_CODE >> '$LOG_FILE'
            
            if [ \$EXIT_CODE -eq 0 ]; then
                echo 'Clean exit - not restarting' >> '$LOG_FILE'
                break
            else
                echo 'Unexpected exit - restarting in 60 seconds...' >> '$LOG_FILE'
                sleep 60
            fi
        done
    " > /dev/null 2>&1 &
    
    # Save PID
    echo $! > "$PID_FILE"
    
    echo -e "${GREEN}✅ Trader started!${NC}"
    echo "PID: $(cat $PID_FILE)"
    echo "Logs: $LOG_FILE"
    echo ""
    echo "Commands:"
    echo "  ./trader_daemon.sh status  - Check status"
    echo "  ./trader_daemon.sh logs    - View logs"
    echo "  ./trader_daemon.sh stop    - Stop trader"
}

# Function to stop trader
stop_trader() {
    echo -e "${YELLOW}🛑 Stopping Alpaca Crypto Trader...${NC}"
    
    if ! is_running; then
        echo -e "${YELLOW}⚠️  Trader is not running${NC}"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    
    # Try graceful shutdown first
    kill "$PID" 2>/dev/null
    
    # Wait up to 10 seconds
    for i in {1..10}; do
        if ! ps -p "$PID" > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done
    
    # Force kill if still running
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Forcing shutdown..."
        kill -9 "$PID" 2>/dev/null
    fi
    
    rm -f "$PID_FILE"
    echo -e "${GREEN}✅ Trader stopped${NC}"
}

# Function to show status
show_status() {
    echo "========================================"
    echo "📊 Alpaca Crypto Trader Status"
    echo "========================================"
    
    if is_running; then
        PID=$(cat "$PID_FILE")
        UPTIME=$(ps -p "$PID" -o etime= 2>/dev/null | xargs)
        echo -e "Status: ${GREEN}RUNNING ✅${NC}"
        echo "PID: $PID"
        echo "Uptime: $UPTIME"
        echo "Log: $LOG_FILE"
    else
        echo -e "Status: ${RED}STOPPED ❌${NC}"
    fi
    
    echo ""
    echo "Recent activity:"
    if [ -f "$LOG_FILE" ]; then
        tail -n 5 "$LOG_FILE"
    else
        echo "No logs yet"
    fi
}

# Function to tail logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        echo "📋 Showing live logs (Ctrl+C to exit)..."
        echo ""
        tail -f "$LOG_FILE"
    else
        echo "❌ No logs found: $LOG_FILE"
    fi
}

# Function to restart trader
restart_trader() {
    stop_trader
    sleep 2
    start_trader
}

# Function to install as system service (macOS launchd)
install_service_mac() {
    echo "🍎 Installing as macOS LaunchAgent..."
    
    PLIST_FILE="$HOME/Library/LaunchAgents/com.alpaca.crypto.trader.plist"
    
    cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.alpaca.crypto.trader</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$SCRIPT_DIR/trader_daemon.sh</string>
        <string>start</string>
    </array>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>ALPACA_API_KEY</key>
        <string>$ALPACA_API_KEY</string>
        <key>ALPACA_SECRET_KEY</key>
        <string>$ALPACA_SECRET_KEY</string>
    </dict>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    
    <key>StandardOutPath</key>
    <string>$LOG_DIR/system.log</string>
    
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/system_error.log</string>
</dict>
</plist>
EOF
    
    # Load the service
    launchctl load "$PLIST_FILE"
    
    echo "✅ Service installed!"
    echo ""
    echo "The trader will now:"
    echo "  - Start automatically when you login"
    echo "  - Restart automatically if it crashes"
    echo "  - Run even when laptop sleeps (if configured)"
    echo ""
    echo "Commands:"
    echo "  launchctl start com.alpaca.crypto.trader   - Start service"
    echo "  launchctl stop com.alpaca.crypto.trader    - Stop service"
    echo "  launchctl unload $PLIST_FILE - Uninstall service"
}

# Function to install as systemd service (Linux)
install_service_linux() {
    echo "🐧 Installing as systemd service..."
    
    SERVICE_FILE="/etc/systemd/system/alpaca-crypto-trader.service"
    
    sudo bash -c "cat > '$SERVICE_FILE'" << EOF
[Unit]
Description=Alpaca Crypto Paper Trader
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
Environment="ALPACA_API_KEY=$ALPACA_API_KEY"
Environment="ALPACA_SECRET_KEY=$ALPACA_SECRET_KEY"
ExecStart=/usr/bin/python3 $TRADER_SCRIPT
Restart=always
RestartSec=60
StandardOutput=append:$LOG_FILE
StandardError=append:$LOG_FILE

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable alpaca-crypto-trader.service
    sudo systemctl start alpaca-crypto-trader.service
    
    echo "✅ Service installed and started!"
    echo ""
    echo "Commands:"
    echo "  sudo systemctl start alpaca-crypto-trader   - Start"
    echo "  sudo systemctl stop alpaca-crypto-trader    - Stop"
    echo "  sudo systemctl status alpaca-crypto-trader  - Status"
    echo "  sudo systemctl restart alpaca-crypto-trader - Restart"
}

# Main command handler
case "${1:-}" in
    start)
        start_trader
        ;;
    stop)
        stop_trader
        ;;
    restart)
        restart_trader
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    install-service)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            install_service_mac
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            install_service_linux
        else
            echo "❌ Unsupported OS: $OSTYPE"
            exit 1
        fi
        ;;
    *)
        echo "Alpaca Crypto Trader Daemon"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs|install-service}"
        echo ""
        echo "Commands:"
        echo "  start           - Start trader in background"
        echo "  stop            - Stop trader"
        echo "  restart         - Restart trader"
        echo "  status          - Check if running"
        echo "  logs            - View live logs"
        echo "  install-service - Install as system service (auto-start on boot)"
        echo ""
        exit 1
        ;;
esac

exit 0
