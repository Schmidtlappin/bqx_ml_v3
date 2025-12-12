#!/bin/bash
#
# BQX-ML-V3 System Health Monitor
# Monitors VM health metrics and alerts on critical conditions
# CREATED 2025-12-11
#
# Usage:
#   ./health-monitor.sh [--continuous] [--interval SECONDS]
#
# Options:
#   --continuous    Run continuous monitoring (default: single check)
#   --interval N    Check every N seconds (default: 300 = 5 minutes)
#   --alert         Send alerts for critical conditions
#

set -e

# Configuration
LOG_DIR="/home/micha/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/health_monitor_$TIMESTAMP.log"

# Thresholds
LOAD_WARNING=20.0
LOAD_CRITICAL=50.0
MEM_WARNING=85
MEM_CRITICAL=95
DISK_WARNING=85
DISK_CRITICAL=95
RCLONE_MAX=2

# Parse arguments
CONTINUOUS=false
INTERVAL=300
ALERT=false

for arg in "$@"; do
    case $arg in
        --continuous)
            CONTINUOUS=true
            shift
            ;;
        --interval)
            INTERVAL="$2"
            shift 2
            ;;
        --alert)
            ALERT=true
            shift
            ;;
    esac
done

# Ensure log directory exists
mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

alert() {
    local severity=$1
    local message=$2
    log "[$severity] $message"
    # Future: Send to monitoring system, Slack, email, etc.
}

check_health() {
    log "=== SYSTEM HEALTH CHECK ==="

    # Load Average
    LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
    LOAD_INT=$(echo "$LOAD" | cut -d'.' -f1)

    if (( $(echo "$LOAD > $LOAD_CRITICAL" | bc -l) )); then
        alert "CRITICAL" "Load average: $LOAD (threshold: $LOAD_CRITICAL)"
    elif (( $(echo "$LOAD > $LOAD_WARNING" | bc -l) )); then
        alert "WARNING" "Load average: $LOAD (threshold: $LOAD_WARNING)"
    else
        log "Load average: $LOAD ✓"
    fi

    # Memory Usage
    MEM_INFO=$(free | grep Mem)
    MEM_TOTAL=$(echo "$MEM_INFO" | awk '{print $2}')
    MEM_USED=$(echo "$MEM_INFO" | awk '{print $3}')
    MEM_PERCENT=$((MEM_USED * 100 / MEM_TOTAL))

    if [ $MEM_PERCENT -ge $MEM_CRITICAL ]; then
        alert "CRITICAL" "Memory usage: ${MEM_PERCENT}% (threshold: ${MEM_CRITICAL}%)"
    elif [ $MEM_PERCENT -ge $MEM_WARNING ]; then
        alert "WARNING" "Memory usage: ${MEM_PERCENT}% (threshold: ${MEM_WARNING}%)"
    else
        log "Memory usage: ${MEM_PERCENT}% ✓"
    fi

    # Swap Usage
    SWAP_INFO=$(free | grep Swap)
    SWAP_TOTAL=$(echo "$SWAP_INFO" | awk '{print $2}')
    SWAP_USED=$(echo "$SWAP_INFO" | awk '{print $3}')

    if [ $SWAP_TOTAL -gt 0 ]; then
        SWAP_PERCENT=$((SWAP_USED * 100 / SWAP_TOTAL))
        if [ $SWAP_USED -gt 0 ]; then
            alert "WARNING" "Swap in use: ${SWAP_PERCENT}% ($(numfmt --to=iec-i --suffix=B $((SWAP_USED * 1024))))"
        else
            log "Swap usage: 0% ✓"
        fi
    fi

    # Disk Usage
    DISK_INFO=$(df -h / | tail -1)
    DISK_PERCENT=$(echo "$DISK_INFO" | awk '{print $5}' | tr -d '%')

    if [ $DISK_PERCENT -ge $DISK_CRITICAL ]; then
        alert "CRITICAL" "Disk usage: ${DISK_PERCENT}% (threshold: ${DISK_CRITICAL}%)"
    elif [ $DISK_PERCENT -ge $DISK_WARNING ]; then
        alert "WARNING" "Disk usage: ${DISK_PERCENT}% (threshold: ${DISK_WARNING}%)"
    else
        log "Disk usage: ${DISK_PERCENT}% ✓"
    fi

    # Active rclone processes
    RCLONE_COUNT=$(ps aux | grep rclone | grep -v grep | wc -l)

    if [ $RCLONE_COUNT -gt $RCLONE_MAX ]; then
        alert "WARNING" "Active rclone processes: $RCLONE_COUNT (threshold: $RCLONE_MAX)"
        log "Listing rclone processes:"
        ps aux | grep rclone | grep -v grep | tee -a "$LOG_FILE"
    else
        log "Active rclone: $RCLONE_COUNT ✓"
    fi

    # Check for stuck processes (in D state - uninterruptible sleep)
    STUCK_COUNT=$(ps -eo stat | grep '^D' | wc -l)
    if [ $STUCK_COUNT -gt 0 ]; then
        alert "WARNING" "Processes in uninterruptible sleep (D state): $STUCK_COUNT"
        log "Stuck processes:"
        ps -eo pid,stat,wchan:20,cmd | grep '^[^ ]* D' | tee -a "$LOG_FILE"
    else
        log "No stuck processes ✓"
    fi

    # Top memory consumers
    log "Top 5 memory consumers:"
    ps aux --sort=-%mem | head -6 | tee -a "$LOG_FILE"

    # Check for zombie processes
    ZOMBIE_COUNT=$(ps -eo stat | grep '^Z' | wc -l)
    if [ $ZOMBIE_COUNT -gt 0 ]; then
        alert "INFO" "Zombie processes detected: $ZOMBIE_COUNT"
    fi

    log "=== HEALTH CHECK COMPLETE ==="
    echo ""
}

main() {
    log "Starting BQX-ML-V3 Health Monitor"
    log "Continuous: $CONTINUOUS | Interval: ${INTERVAL}s | Alert: $ALERT"

    if [ "$CONTINUOUS" = true ]; then
        while true; do
            check_health
            sleep $INTERVAL
        done
    else
        check_health
    fi

    log "Health monitor finished"
}

# Run main
main
