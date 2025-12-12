# SSH Connection Troubleshooting Guide
## bqx-ml-master (GCP Compute Engine)

**Last Updated**: December 11, 2025
**Instance**: bqx-ml-master
**IP**: 34.139.203.254
**Port**: 22

---

## Quick Diagnostics

### From Windows PowerShell:

```powershell
# Test network connectivity
Test-NetConnection -ComputerName 34.139.203.254 -Port 22

# Should show: TcpTestSucceeded : True
```

### From Command Prompt or PowerShell:

```bash
# Test SSH connection (verbose mode)
ssh -v bqx-ml-master

# Test with timeout
ssh -o ConnectTimeout=10 bqx-ml-master "uptime"
```

---

## Common Issues & Solutions

### Issue 1: Connection Timeout

**Symptoms:**
```
ssh: connect to host bqx-ml-master port 22: Connection timed out
```

**Causes:**
- VM is under heavy load (check GCP Console)
- Network/firewall blocking connection
- VPN interfering with connection

**Solutions:**

1. **Check VM Status via GCP Console:**
   ```
   https://console.cloud.google.com/compute/instances
   ```
   - Verify instance is running
   - Check CPU/memory usage

2. **Try Direct IP:**
   ```bash
   ssh micha@34.139.203.254
   ```

3. **Disable VPN temporarily:**
   - Norton VPN may interfere
   - Disconnect and retry

4. **Check firewall rules:**
   ```bash
   # From PowerShell (as admin)
   netsh advfirewall show allprofiles
   ```

### Issue 2: Permission Denied (publickey)

**Symptoms:**
```
Permission denied (publickey).
```

**Causes:**
- SSH key not found or incorrect
- Wrong username
- Key permissions too open

**Solutions:**

1. **Verify SSH key exists:**
   ```bash
   dir C:\Users\micha\.ssh\google_compute_engine
   ```

2. **Check SSH config:**
   ```bash
   type C:\Users\micha\.ssh\config
   ```
   Should contain:
   ```
   Host bqx-ml-master
       HostName 34.139.203.254
       User micha
       IdentityFile C:\Users\micha\.ssh\google_compute_engine
   ```

3. **Regenerate key if needed:**
   ```bash
   gcloud compute config-ssh
   ```

4. **Fix key permissions (Windows):**
   ```powershell
   icacls C:\Users\micha\.ssh\google_compute_engine /inheritance:r
   icacls C:\Users\micha\.ssh\google_compute_engine /grant:r "$env:USERNAME:R"
   ```

### Issue 3: Connection Refused

**Symptoms:**
```
ssh: connect to host 34.139.203.254 port 22: Connection refused
```

**Causes:**
- SSH daemon not running on VM
- Wrong port
- VM firewall blocking

**Solutions:**

1. **Check via GCP Serial Console:**
   - Go to GCP Console → VM Instance → Serial Console
   - Login and check: `sudo systemctl status sshd`

2. **Restart SSH daemon:**
   ```bash
   sudo systemctl restart sshd
   ```

3. **Check firewall on VM:**
   ```bash
   sudo ufw status
   sudo iptables -L | grep 22
   ```

### Issue 4: Connection Established then Hangs

**Symptoms:**
```
debug1: Connection established.
debug1: Authenticating...
[hangs here]
```

**Causes:**
- VM under extreme load
- Out of memory
- SSH daemon maxed out connections

**Solutions:**

1. **Check VM health:**
   - Use GCP Console → Monitoring
   - CPU > 80%? Memory > 95%?

2. **Kill stuck processes via GCP Serial Console:**
   ```bash
   # Login via serial console
   ps aux --sort=-%mem | head -10
   sudo kill -9 <PID>
   ```

3. **Reboot VM if unresponsive:**
   ```bash
   # Via GCP Console
   COMPUTE ENGINE → VM INSTANCES → bqx-ml-master → RESET
   ```

---

## Alternative Connection Methods

### Method 1: GCP Serial Console (Always Available)

1. Go to: https://console.cloud.google.com/compute/instances
2. Click on `bqx-ml-master`
3. Click `CONNECT` → `Connect to serial console`
4. Login with username/password (not SSH key)

### Method 2: GCP IAP Tunnel

```bash
gcloud compute ssh bqx-ml-master --tunnel-through-iap
```

### Method 3: VS Code Remote SSH

1. Install "Remote - SSH" extension
2. Open Command Palette (Ctrl+Shift+P)
3. Select "Remote-SSH: Connect to Host"
4. Enter: `bqx-ml-master`

---

## Current VM Health Status

As of 2025-12-11 21:13 UTC:

| Metric | Value | Status |
|--------|-------|--------|
| Load Average | 22.18 | ⚠️ WARNING |
| Memory Usage | 94% | ⚠️ CRITICAL |
| Swap Usage | 78% (13GB) | ⚠️ CRITICAL |
| Stuck Processes | 7 (D state) | ⚠️ WARNING |
| Active rclone | 0 | ✅ OK |

**Recommendation**: VM is under severe stress. SSH connections may timeout. Consider:
1. Killing stuck Python processes (PIDs 235285, 235564)
2. Dropping caches to free memory
3. Rebooting if issues persist

---

## Emergency Access (If SSH Completely Fails)

### Option 1: GCP Console Reset

```
1. Go to: https://console.cloud.google.com/compute/instances
2. Select bqx-ml-master
3. Click RESET (hard reboot)
4. Wait 2-3 minutes
5. Retry SSH connection
```

### Option 2: Stop/Start Instance

```
1. Go to: https://console.cloud.google.com/compute/instances
2. Select bqx-ml-master
3. Click STOP
4. Wait for full stop
5. Click START
6. Note: External IP may change
```

### Option 3: Create New SSH Key

```bash
# Generate new key
ssh-keygen -t rsa -f C:\Users\micha\.ssh\bqx-ml-master-new -C micha

# Add to GCP via console
# Compute Engine → Metadata → SSH Keys → Add SSH key

# Update SSH config
# IdentityFile C:\Users\micha\.ssh\bqx-ml-master-new
```

---

## Monitoring & Prevention

### Check VM Health Before Connecting

```bash
# From GCP Console: Monitoring tab
# Or use gcloud CLI:
gcloud compute instances describe bqx-ml-master --format="get(status)"
```

### Automated Health Checks

```bash
# Run health monitor (if SSH works)
ssh bqx-ml-master "/home/micha/bqx_ml_v3/scripts/health-monitor.sh"
```

### Keep Alive for Long Sessions

Add to `~/.ssh/config` (Windows: `C:\Users\micha\.ssh\config`):

```
Host bqx-ml-master
    ServerAliveInterval 60
    ServerAliveCountMax 3
    TCPKeepAlive yes
```

---

## Contact & Escalation

| Issue | Action |
|-------|--------|
| Cannot connect after 3 attempts | Check GCP Console, try Serial Console |
| VM appears stopped/frozen | Use GCP Console to check status |
| Network timeout | Check VPN, firewall, local network |
| Persistent issues | Contact GCP Support |

---

## Related Documentation

- [VM Health Maintenance Guide](VM_HEALTH_MAINTENANCE_GUIDE.md)
- [SSH Config](../../C:/Users/micha/.ssh/config)
- [GCP Console - Compute Instances](https://console.cloud.google.com/compute/instances?project=bqx-ml)

---

**END OF GUIDE**
