# SSH Remote Host Configuration for bqx-ml-master

**Purpose**: SSH configuration details to connect from Windows local instance to GCP bqx-ml-master
**Created**: 2025-11-25
**Status**: Ready for GitHub Secrets

---

## 🖥️ Host Information

### GCP Compute Instance
- **Instance Name**: bqx-ml-master
- **Zone**: us-east1-b
- **Project**: bqx-ml
- **External IP**: 34.148.152.67
- **Internal IP**: 10.142.0.3
- **OS**: Debian GNU/Linux
- **Machine Type**: n1-standard-4 (or similar)

---

## 🔐 SSH Configuration

### For Windows OpenSSH Client

**Config File Location**: `C:\Users\<YourUsername>\.ssh\config`

**Configuration**:
```ssh-config
Host bqx-ml-master
    HostName 34.148.152.67
    User micha
    Port 22
    IdentityFile ~/.ssh/google_compute_engine
    ServerAliveInterval 60
    ServerAliveCountMax 3
    StrictHostKeyChecking no
    UserKnownHostsFile ~/.ssh/known_hosts
```

### For Windows PuTTY

**Session Configuration**:
```
Host Name: 34.148.152.67
Port: 22
Connection Type: SSH
Saved Sessions: bqx-ml-master
```

**Connection > Data**:
```
Auto-login username: micha
```

**Connection > SSH > Auth**:
```
Private key file: C:\Users\<YourUsername>\.ssh\google_compute_engine.ppk
```

**Connection > SSH > Keepalives**:
```
Seconds between keepalives: 60
```

---

## 📦 GitHub Secrets to Add

### Option 1: Individual Secrets

Add these as separate GitHub secrets:

1. **SSH_HOST_IP**
   ```
   34.148.152.67
   ```

2. **SSH_HOST_USER**
   ```
   micha
   ```

3. **SSH_HOST_PORT**
   ```
   22
   ```

4. **SSH_HOST_ZONE**
   ```
   us-east1-b
   ```

5. **SSH_PRIVATE_KEY**
   ```
   # Content of your private key (~/.ssh/google_compute_engine)
   # This should be the actual private key content, not a path
   -----BEGIN OPENSSH PRIVATE KEY-----
   <your-private-key-content-here>
   -----END OPENSSH PRIVATE KEY-----
   ```

### Option 2: Single JSON Secret

Add this as a single JSON secret named **SSH_REMOTE_HOST_CONFIG**:

```json
{
  "host": "bqx-ml-master",
  "hostname": "34.148.152.67",
  "internal_ip": "10.142.0.3",
  "user": "micha",
  "port": 22,
  "zone": "us-east1-b",
  "project": "bqx-ml",
  "identity_file": "~/.ssh/google_compute_engine",
  "server_alive_interval": 60,
  "server_alive_count_max": 3,
  "strict_host_key_checking": false,
  "connection_timeout": 30,
  "ssh_config": "Host bqx-ml-master\n    HostName 34.148.152.67\n    User micha\n    Port 22\n    IdentityFile ~/.ssh/google_compute_engine\n    ServerAliveInterval 60\n    ServerAliveCountMax 3"
}
```

---

## 🔧 Setup Instructions

### Windows OpenSSH Client Setup

#### 1. Install OpenSSH Client (if not already installed)
```powershell
# Run in PowerShell as Administrator
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
```

#### 2. Create SSH Config File
```powershell
# Create .ssh directory if it doesn't exist
New-Item -ItemType Directory -Path "$env:USERPROFILE\.ssh" -Force

# Create/edit config file
notepad "$env:USERPROFILE\.ssh\config"
```

#### 3. Add Configuration
Paste the SSH config from above into the file and save.

#### 4. Set Correct Permissions
```powershell
# Set correct permissions on config file
icacls "$env:USERPROFILE\.ssh\config" /inheritance:r
icacls "$env:USERPROFILE\.ssh\config" /grant:r "$env:USERNAME:(R)"
```

#### 5. Add Private Key
Copy your GCP SSH private key to:
```
C:\Users\<YourUsername>\.ssh\google_compute_engine
```

Or generate a new key:
```powershell
ssh-keygen -t rsa -b 4096 -f "$env:USERPROFILE\.ssh\google_compute_engine" -C "micha@bqx-ml-master"
```

Then add the public key to the GCP instance:
```powershell
# Copy public key to clipboard
Get-Content "$env:USERPROFILE\.ssh\google_compute_engine.pub" | Set-Clipboard
```

Go to GCP Console → Compute Engine → VM Instances → bqx-ml-master → Edit → SSH Keys → Add Item

#### 6. Test Connection
```powershell
ssh bqx-ml-master
```

### VS Code Remote SSH Setup

#### 1. Install Extension
Install "Remote - SSH" extension in VS Code

#### 2. Configure Remote Host
1. Press `Ctrl+Shift+P`
2. Type "Remote-SSH: Connect to Host"
3. Select "Configure SSH Hosts"
4. Choose `C:\Users\<YourUsername>\.ssh\config`
5. Add the configuration from above
6. Save file

#### 3. Connect
1. Press `Ctrl+Shift+P`
2. Type "Remote-SSH: Connect to Host"
3. Select "bqx-ml-master"
4. VS Code will connect to the remote host

---

## 🚀 Quick Connect Commands

### From Windows Command Prompt
```cmd
ssh bqx-ml-master
```

### From Windows PowerShell
```powershell
ssh bqx-ml-master
```

### With Specific Key
```cmd
ssh -i "C:\Users\<YourUsername>\.ssh\google_compute_engine" micha@34.148.152.67
```

### With Port Forwarding (for Jupyter, etc.)
```cmd
ssh -L 8888:localhost:8888 bqx-ml-master
```

---

## 📝 Adding to GitHub Secrets

### Via GitHub CLI (gh)

```powershell
# Set individual secrets
gh secret set SSH_HOST_IP --body "34.148.152.67"
gh secret set SSH_HOST_USER --body "micha"
gh secret set SSH_HOST_PORT --body "22"
gh secret set SSH_HOST_ZONE --body "us-east1-b"

# Set JSON config (from file)
gh secret set SSH_REMOTE_HOST_CONFIG < ssh_config.json

# Set SSH private key (from file)
gh secret set SSH_PRIVATE_KEY < ~/.ssh/google_compute_engine
```

### Via GitHub Web Interface

1. Go to: https://github.com/Schmidtlappin/bqx_ml_v3/settings/secrets/actions
2. Click "New repository secret"
3. Name: `SSH_REMOTE_HOST_CONFIG`
4. Value: Copy the JSON from "Option 2" above
5. Click "Add secret"

For the private key:
1. Click "New repository secret"
2. Name: `SSH_PRIVATE_KEY`
3. Value: Paste the entire content of your private key file
4. Click "Add secret"

---

## 🔒 Security Best Practices

### 1. Private Key Protection
- **Never commit** private keys to git
- Store private keys with restricted permissions
- Use different keys for different environments

### 2. Key Rotation
- Rotate SSH keys every 90 days
- Remove old keys from GCP instance
- Update GitHub secrets with new keys

### 3. Access Control
- Limit SSH access to specific IP ranges (optional)
- Use GCP IAP for additional security layer
- Enable 2FA on GitHub account

### 4. Monitoring
- Monitor SSH login attempts
- Set up alerts for failed logins
- Regular audit of authorized keys

---

## 🛠️ Troubleshooting

### Connection Refused
```powershell
# Check if instance is running
gcloud compute instances describe bqx-ml-master --zone=us-east1-b

# Check firewall rules
gcloud compute firewall-rules list --filter="name~ssh"
```

### Permission Denied
```powershell
# Check key permissions
icacls "$env:USERPROFILE\.ssh\google_compute_engine"

# Should show only your username with Read permissions
```

### Host Key Verification Failed
```powershell
# Remove old host key
ssh-keygen -R 34.148.152.67

# Or clear known_hosts
Remove-Item "$env:USERPROFILE\.ssh\known_hosts"
```

### Timeout Issues
```powershell
# Test connectivity
Test-NetConnection -ComputerName 34.148.152.67 -Port 22

# Check if SSH service is running on remote
gcloud compute ssh bqx-ml-master --zone=us-east1-b --command="sudo systemctl status ssh"
```

---

## 📊 Connection Test Script

**File**: `scripts/test_ssh_connection.ps1`

```powershell
# Test SSH connection to bqx-ml-master
# Run from Windows PowerShell

$hostname = "34.148.152.67"
$user = "micha"
$port = 22

Write-Host "Testing SSH connection to bqx-ml-master..." -ForegroundColor Cyan

# Test 1: Network connectivity
Write-Host "`n1. Testing network connectivity..." -ForegroundColor Yellow
$pingResult = Test-NetConnection -ComputerName $hostname -Port $port

if ($pingResult.TcpTestSucceeded) {
    Write-Host "   ✓ Port $port is reachable" -ForegroundColor Green
} else {
    Write-Host "   ✗ Port $port is NOT reachable" -ForegroundColor Red
    exit 1
}

# Test 2: SSH key exists
Write-Host "`n2. Checking SSH private key..." -ForegroundColor Yellow
$keyPath = "$env:USERPROFILE\.ssh\google_compute_engine"

if (Test-Path $keyPath) {
    Write-Host "   ✓ Private key found at $keyPath" -ForegroundColor Green
} else {
    Write-Host "   ✗ Private key NOT found at $keyPath" -ForegroundColor Red
    Write-Host "   Generate key with: ssh-keygen -t rsa -b 4096 -f $keyPath" -ForegroundColor Yellow
    exit 1
}

# Test 3: SSH config exists
Write-Host "`n3. Checking SSH config..." -ForegroundColor Yellow
$configPath = "$env:USERPROFILE\.ssh\config"

if (Test-Path $configPath) {
    $configContent = Get-Content $configPath -Raw
    if ($configContent -match "Host bqx-ml-master") {
        Write-Host "   ✓ SSH config found with bqx-ml-master host" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ SSH config found but missing bqx-ml-master host" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠ SSH config NOT found at $configPath" -ForegroundColor Yellow
}

# Test 4: Attempt connection
Write-Host "`n4. Testing SSH connection..." -ForegroundColor Yellow
$sshTest = ssh -o ConnectTimeout=10 -o BatchMode=yes -i $keyPath "$user@$hostname" "echo 'Connection successful'" 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ SSH connection successful!" -ForegroundColor Green
    Write-Host "   Message from server: $sshTest" -ForegroundColor Cyan
} else {
    Write-Host "   ✗ SSH connection failed" -ForegroundColor Red
    Write-Host "   Error: $sshTest" -ForegroundColor Red
}

Write-Host "`nConnection test complete.`n" -ForegroundColor Cyan
```

---

## 🔗 Related Resources

### GCP Documentation
- [Connecting to instances](https://cloud.google.com/compute/docs/instances/connecting-to-instance)
- [Managing SSH keys](https://cloud.google.com/compute/docs/instances/adding-removing-ssh-keys)
- [OS Login](https://cloud.google.com/compute/docs/oslogin)

### GitHub Documentation
- [Encrypted secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Using secrets in workflows](https://docs.github.com/en/actions/security-guides/encrypted-secrets#using-encrypted-secrets-in-a-workflow)

### SSH Documentation
- [OpenSSH Config File](https://www.ssh.com/academy/ssh/config)
- [PuTTY Documentation](https://www.chiark.greenend.org.uk/~sgtatham/putty/docs.html)

---

## ✅ Verification Checklist

- [ ] SSH config created at `~/.ssh/config`
- [ ] Private key exists and has correct permissions
- [ ] Public key added to GCP instance
- [ ] Test connection successful
- [ ] VS Code Remote SSH configured (optional)
- [ ] GitHub secrets added
- [ ] Documentation reviewed

---

*Document Version: 1.0*
*Created: 2025-11-25*
*Author: BQXML Chief Engineer*
