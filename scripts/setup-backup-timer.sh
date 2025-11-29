#!/bin/bash
#
# Setup BQX-ML-V3 Automatic Backup Timer
# Installs systemd service and timer for daily backups
#
# Run as: sudo ./setup-backup-timer.sh
#

set -e

CONFIG_DIR="/home/micha/bqx_ml_v3/configs"
SYSTEMD_DIR="/etc/systemd/system"

echo "=== BQX-ML-V3 Backup Timer Setup ==="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

# Copy service and timer files
echo "Installing systemd service..."
cp "$CONFIG_DIR/bqx-backup.service" "$SYSTEMD_DIR/"
cp "$CONFIG_DIR/bqx-backup.timer" "$SYSTEMD_DIR/"

# Reload systemd
echo "Reloading systemd..."
systemctl daemon-reload

# Enable and start timer
echo "Enabling backup timer..."
systemctl enable bqx-backup.timer
systemctl start bqx-backup.timer

# Show status
echo ""
echo "=== Timer Status ==="
systemctl status bqx-backup.timer --no-pager

echo ""
echo "=== Next Scheduled Run ==="
systemctl list-timers bqx-backup.timer --no-pager

echo ""
echo "Setup complete!"
echo ""
echo "Commands:"
echo "  View timer status:  systemctl status bqx-backup.timer"
echo "  View service logs:  journalctl -u bqx-backup.service"
echo "  Manual run:         systemctl start bqx-backup.service"
echo "  Disable timer:      systemctl disable bqx-backup.timer"
