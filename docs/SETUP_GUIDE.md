# CYFER ULTIMATE GHOST TOOLKIT v3.0 - SETUP GUIDE

## PREREQUISITES
- Termux (latest version from F-Droid)
- Android 8.0 or higher
- Minimum 2GB RAM (4GB recommended)
- At least 500MB free storage

## INSTALLATION

### Step 1: Initial Setup
```bash
termux-setup-storage
pkg update -y && pkg upgrade -y
pkg install git -y
```

### Step 2: Clone Repository
```bash
git clone https://github.com/your-repo/cyfer_toolkit.git
~/cyfer_toolkit
cd ~/cyfer_toolkit
```

### Step 3: Run Installer
```bash
chmod +x scripts/install_dependencies.sh
./scripts/install_dependencies.sh
```

### Step 4: Configure Environment
```bash
chmod +x scripts/configure_environment.sh
./scripts/configure_environment.sh
```

### Step 5: Start CYFER
```bash
chmod +x scripts/start_cyfer.sh
./scripts/start_cyfer.sh
```

## VERIFICATION
After installation, verify all services are running:
```bash
./scripts/test_leaks.sh
```

## TROUBLESHOOTING
If you encounter issues:
1. Check logs: `tail -f ~/.cyfer/logs/cyfer.log`
2. Restart services: `./scripts/stop_cyfer.sh &&
./scripts/start_cyfer.sh`
3. For complete reinstall, run: `./scripts/emergency_nuke.sh
--confirm`
```
