# CYFER ULTIMATE GHOST TOOLKIT v0.1 - TROUBLESHOOTING

## COMMON ISSUES

### 1. Tor Fails to Start
**Symptoms**:
- "Failed to start Tor" error
- No connection through SOCKS proxy

**Solutions**:
```bash
# Check if Tor port is already in use
netstat -tulpn | grep 9050

# Kill conflicting processes
pkill tor

# Restart Tor manually
tor -f ~/torrc
```

### 2. DNS Leaks
**Symptoms**:
- Real IP visible in DNS leak tests
- DNS queries not going through Tor

**Solutions**:
```bash
# Check DNSCrypt status
pgrep dnscrypt-proxy

# Restart DNSCrypt
pkill dnscrypt-proxy
dnscrypt-proxy -config
/data/data/com.termux/files/usr/etc/dnscrypt-proxy.toml
```

### 3. High CPU/Memory Usage
**Symptoms**:
- Device becomes slow
- High resource usage in task manager

**Solutions**:
```bash
# Identify resource-heavy processes
top

# Kill unnecessary processes
pkill -f "python.*unnecessary_script"

# Adjust resource limits in config
nano ~/.cyfer/config/settings.json
```

## EMERGENCY PROCEDURES

### Complete System Reset
```bash
./scripts/emergency_nuke.sh
```

### Reinstall from Scratch
```bash
./scripts/emergency_nuke.sh --confirm
cd ~
rm -rf cyfer_toolkit
git clone https://github.com/your-repo/cyfer_toolkit.git
cd cyfer_toolkit
./scripts/install_dependencies.sh
./scripts/configure_environment.sh
```
