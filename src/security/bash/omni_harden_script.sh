#!/usr/bin/env bash
# OMNI Security Hardening Script for Linux Nodes

set -euo pipefail

echo "[OMNI Security] Starting Node Hardening Sequence"

# Disable IP Forwarding
sysctl -w net.ipv4.ip_forward=0
echo "net.ipv4.ip_forward = 0" >> /etc/sysctl.conf

# Disable ICMP Redirects
sysctl -w net.ipv4.conf.all.accept_redirects=0
sysctl -w net.ipv6.conf.all.accept_redirects=0

# Configure UFW firewall
if command -v ufw >/dev/null; then
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow 8080/tcp # OMNI gRPC Proxy
    ufw allow 443/tcp  # HTTPS
    ufw --force enable
fi

echo "[OMNI Security] Node Hardening Complete"
