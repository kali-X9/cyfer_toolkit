#!/bin/bash
# CYFER ULTIMATE GHOST TOOLKIT - STOP SCRIPT

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}[*] Stopping CYFER Ultimate Ghost
Toolkit...${NC}"

# Stop Python processes
pkill -f "python.*main.py"

# Stop Tor
pkill -f "tor.*-f ~/torrc"

# Stop V2Ray
pkill -f "v2ray.*-config"

# Stop DNSCrypt
pkill -f "dnscrypt-proxy"

echo -e "${GREEN}[+] CYFER services stopped!${NC}"
```
