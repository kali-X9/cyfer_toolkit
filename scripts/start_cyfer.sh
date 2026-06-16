#!/bin/bash
# CYFER ULTIMATE GHOST TOOLKIT - START SCRIPT

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if already running
if pgrep -f "python.*main.py" > /dev/null; then
    echo -e "${YELLOW}[!] CYFER is already running!${NC}"
    exit 1
fi

echo -e "${YELLOW}[*] Starting CYFER Ultimate Ghost
Toolkit...${NC}"

# Start services in background
nohup python ~/cyfer_toolkit/src/main.py >
~/.cyfer/logs/cyfer.log 2>&1 &

# Wait for services to initialize
sleep 5

# Check if services started successfully
if pgrep -f "python.*main.py" > /dev/null; then
    echo -e "${GREEN}[+] CYFER started successfully!${NC}"
    echo -e "${YELLOW}[*] Use 'tail -f ~/.cyfer/logs/cyfer.log'
to view logs${NC}"
else
    echo -e "${RED}[-] Failed to start CYFER! Check logs for
details.${NC}"
    exit 1
fi
```
