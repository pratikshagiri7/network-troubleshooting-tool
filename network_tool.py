#!/usr/bin/env python3
"""
🔍 Zscaler Network Troubleshooting Tool
Production CLI for Graduate Trainee Engineer role
TCP/IP · DNS · Port Scanning · Cross-platform
"""

import socket
import subprocess
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor
import platform

def ping_host(host):
    """Ping host (ICMP) - Zscaler core skill"""
    try:
        param = '-n' if platform.system() == 'Windows' else '-c'
        cmd = ['ping', param, '1', '-W', '5', host]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # Extract RTT
            output = result.stdout.lower()
            rtt = "N/A"
            if "time" in output:
                for line in output.split('\n'):
                    if "time" in line:
                        rtt = line.split("time=")[-1].split()[0]
                        break
            return f"🟢 {host}: UP (RTT: {rtt})"
        return f"🔴 {host}: DOWN"
    except:
        return f"⏰ {host}: TIMEOUT"

def dns_lookup(host):
    """DNS Resolution - Zscaler requirement"""
    try:
        ip = socket.gethostbyname(host)
        return f"🌐 {host}: {ip}"
    except socket.gaierror:
        return f"❌ {host}: DNS FAIL"

def port_check(host, port):
    """Port scan (TCP Connect) - Telnet/NMAP equivalent"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        status = "OPEN" if result == 0 else "CLOSED"
        return f"🔌 {host}:{port}: {status}"
    except:
        return f"❌ {host}:{port}: ERROR"

def main():
    parser = argparse.ArgumentParser(description="🔍 Zscaler Network Troubleshooting Tool")
    parser.add_argument('targets', nargs='+', help="Hosts: google.com 8.8.8.8")
    parser.add_argument('--ports', nargs='*', type=int, default=[80, 443], help="Ports to scan")
    args = parser.parse_args()
    
    print("🔍 ZSCALER NETWORK DIAGNOSTICS\n")
    print(f"Targets: {', '.join(args.targets)}")
    print(f"Ports: {args.ports}\n")
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for target in args.targets:
            futures.append(executor.submit(ping_host, target))
            futures.append(executor.submit(dns_lookup, target))
            for port in args.ports:
                futures.append(executor.submit(port_check, target, port))
        
        for future in futures:
            print(future.result())

if __name__ == "__main__":
    main()
