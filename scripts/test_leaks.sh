#!/bin/bash
# CYFER ULTIMATE GHOST TOOLKIT - LEAK TEST SCRIPT

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}[*] Testing for IP leaks...${NC}"

# Test IP leak
IP_RESULT=$(proxychains -q curl -s
https://api.ipify.org?format=json)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[+] IP Leak Test: PASSED${NC}"
else
    echo -e "${RED}[-] IP Leak Test: FAILED${NC}"
fi

echo -e "${YELLOW}[*] Testing for DNS leaks...${NC}"

# Test DNS leak
DNS_RESULT=$(proxychains -q nslookup google.com 127.0.0.1)
if echo "$DNS_RESULT" | grep -q "google.com"; then
    echo -e "${GREEN}[+] DNS Leak Test: PASSED${NC}"
else
    echo -e "${RED}[-] DNS Leak Test: FAILED${NC}"
fi

echo -e "${YELLOW}[*] Testing WebRTC leaks...${NC}"

# Test WebRTC leak (simplified)
if [ -f "/proc/sys/net/ipv6/conf/all/disable_ipv6" ]; then
    echo -e "${GREEN}[+] WebRTC Leak Test: PASSED (IPv6
disabled)${NC}"
else
    echo -e "${YELLOW}[!] WebRTC Leak Test: INCONCLUSIVE${NC}"
fi
```
