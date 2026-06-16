#!/bin/bash
# CYFER ULTIMATE GHOST TOOLKIT - PORT ROTATION SCRIPT

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}[*] Rotating service ports...${NC}"

# Send rotation signal to main process
pkill -SIGUSR1 -f "python.*main.py"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[+] Port rotation signal sent!${NC}"
else
    echo -e "${RED}[-] Failed to send rotation signal!${NC}"
    exit 1
fi
```
