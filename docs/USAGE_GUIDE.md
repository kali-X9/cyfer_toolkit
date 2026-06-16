# CYFER ULTIMATE GHOST TOOLKIT v3.0 - USAGE GUIDE

## BASIC COMMANDS
- Start CYFER: `./start_cyfer.sh`
- Stop CYFER: `./stop_cyfer.sh`
- Rotate IP: `./rotate_ports.sh`
- Test for leaks: `./test_leaks.sh`
- Emergency shutdown: `./emergency_nuke.sh`

## INTERACTIVE MENU
Run the interactive menu:
```bash
python src/cli/interactive_menu.py
```

### Menu Options
1. Start Anonymity Services
2. Stop Anonymity Services
3. Rotate IP Address
4. Test Anonymity
5. Launch Secure Browser
6. System Status
7. Kill Switch (EMERGENCY)
0. Exit

## ADVANCED FEATURES
- Custom bridge configuration: Edit
`~/.cyfer/config/bridges.conf`
- Port configuration: Modify
`~/.cyfer/config/ports.json`
- Log settings: Adjust `~/.cyfer/config/logging.conf`

## SECURITY BEST PRACTICES
1. Always verify your anonymity with `./test_leaks.sh`
2. Regularly update the toolkit: `git pull`
3. Use the kill switch in case of suspected compromise
4. Never run as root
5. Keep your device physically secure
```
