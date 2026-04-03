# Simulates real-world network diagnostics used in enterprise environments
#!/usr/bin/env python3
"""
🔍 🔍 Network Troubleshooting Tool (Zscaler-Inspired)
Production-Level Network Diagnostics CLI Tool
# Designed to handle multiple targets efficiently using multithreading
TCP/IP · DNS · Port Scanning · Traceroute · Multithreading
"""

import socket
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor
import platform

# ---------------------- VALIDATION ----------------------
def validate_host(host):
    try:
        socket.gethostbyname(host)
        return True
    except Exception:
        return False

# ---------------------- PING ----------------------
def ping_host(host):
    """Ping host (ICMP)"""
    try:
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        cmd = ['ping', param, '1', host]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            output = result.stdout.lower()
            rtt = "N/A"

            if "time" in output:
                for line in output.split('\n'):
                    if "time" in line:
                        try:
                            rtt = line.split("time=")[-1].split()[0]
                        except:
                            pass
                        break

            return f"🟢 {host}: UP (RTT: {rtt})"
        else:
            return f"🔴 {host}: DOWN"

    except Exception as e:
        return f"❌ Ping Error ({host}): {str(e)}"

# ---------------------- DNS LOOKUP ----------------------
def dns_lookup(host):
    """DNS Resolution"""
    try:
        ip = socket.gethostbyname(host)
        return f"🌐 {host}: {ip}"
    except socket.gaierror:
        return f"❌ {host}: DNS FAIL"
    except Exception as e:
        return f"❌ DNS Error ({host}): {str(e)}"

# ---------------------- PORT CHECK ----------------------
def port_check(host, port):
    """TCP Port Check"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(3)
            result = sock.connect_ex((host, port))

            status = "OPEN" if result == 0 else "CLOSED"
            return f"🔌 {host}:{port}: {status}"

    except Exception as e:
        return f"❌ Port Error ({host}:{port}): {str(e)}"

# ---------------------- TRACEROUTE ----------------------
def traceroute(host):
    """Traceroute"""
    try:
        cmd = ['tracert', host] if platform.system().lower() == 'windows' else ['traceroute', host]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return f"\n🛰️ Traceroute for {host}:\n{result.stdout}"
    except Exception as e:
        return f"❌ Traceroute Error ({host}): {str(e)}"

# ---------------------- MAIN ----------------------
def main():
    parser = argparse.ArgumentParser(
        description="🔍 Zscaler Network Troubleshooting Tool"
    )
    parser.add_argument(
        'targets',
        nargs='+',
        help="Hosts: google.com 8.8.8.8"
    )
    parser.add_argument(
        '--ports',
        nargs='*',
        type=int,
        default=[80, 443],
        help="Ports to scan"
    )

    args = parser.parse_args()

    print("\n🔍 ZSCALER NETWORK DIAGNOSTICS\n")
    print(f"Targets: {', '.join(args.targets)}")
    print(f"Ports: {args.ports}\n")

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []

        for target in args.targets:

            if not validate_host(target):
                print(f"❌ {target}: INVALID HOST\n")
                continue

            print("\n" + "="*50)
            print(f"🔎 Results for {target}")
            print("="*50)

            futures.append(executor.submit(ping_host, target))
            futures.append(executor.submit(dns_lookup, target))

            for port in args.ports:
                futures.append(executor.submit(port_check, target, port))

        # Print results
        for future in futures:
            print(future.result())

    # Traceroute (separately for clarity)
    for target in args.targets:
        if validate_host(target):
            print(traceroute(target))


# ---------------------- ENTRY POINT ----------------------
if __name__ == "__main__":
    main()
