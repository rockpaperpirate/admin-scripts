import os
import re

def is_valid_ip_or_cidr(addr):
    if not addr or '0.0.0.0' in addr:
        return False
    return re.match(r'^(\d{1,3}\.){3}\d{1,3}(/\d{1,2})?$', addr) is not None

def is_valid_protocol(proto):
    return proto.lower() in ['tcp', 'udp', 'icmp']

def is_valid_port(port):
    try:
        p = int(port)
        return 0 < p <= 65535
    except ValueError:
        return False

def parse_iptables_file(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r') as f:
        lines = f.readlines()
        return [line.strip() for line in lines if line.strip() and not line.startswith('#')]

def interactive_custom_rule_builder(debug=False):
    rules = []
    print("\n== Interactive IPTABLES RULE CREATOR ==")
    while True:
        direction = input("\nChain to add rule to (INPUT/FORWARD): ").strip().upper()
        if not direction:
            break
        if direction not in ['INPUT', 'FORWARD']:
            print("Invalid chain.")
            continue

        addr_type = input("Source or Destination IP? (src/dst): ").strip().lower()
        if addr_type not in ['src', 'dst']:
            print("Must be 'src' or 'dst'.")
            continue

        ip = input("Enter IP or CIDR (no 0.0.0.0): ").strip()
        if not is_valid_ip_or_cidr(ip):
            print("Invalid IP.")
            continue

        proto = input("Protocol (tcp/udp/icmp): ").strip().lower()
        if not is_valid_protocol(proto):
            print("Invalid protocol.")
            continue

        port = None
        if proto in ['tcp', 'udp']:
            port = input("Port (1–65535): ").strip()
            if not is_valid_port(port):
                print("Invalid port.")
                continue

        rule = f"iptables -A {direction} -p {proto}"
        rule += f" -s {ip}" if addr_type == 'src' else f" -d {ip}"
        if port:
            rule += f" --dport {port}"
        rule += " -j ACCEPT"

        if debug:
            print(f"[DEBUG] {rule}")
        rules.append(rule)

    return rules

def confirm_policy_drop():
    confirm = input("Set default policy to DROP for INPUT and FORWARD? (y/N): ").lower()
    if confirm == 'y':
        return [
            "iptables -P INPUT DROP",
            "iptables -P FORWARD DROP"
        ]
    return []

def confirm_and_display_rules(rules):
    print("\n====== RULES TO APPLY ======")
    for r in rules:
        print(r)
    print("============================")
    confirm = input("Proceed with applying these rules? (y/N): ").lower()
    return confirm == 'y'
