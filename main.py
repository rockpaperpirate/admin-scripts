from firewall import (
    parse_iptables_file,
    interactive_custom_rule_builder,
    confirm_policy_drop,
    confirm_and_display_rules
)

from ssh import push_iptables_config
from config import load_config, get_host_config

def build_rules(debug=False):
    rules = []

    file_path = input("Path to iptables rule file (leave empty to skip): ").strip()
    if file_path:
        rules += parse_iptables_file(file_path)

    if input("Add custom rules interactively? (y/N): ").lower() == 'y':
        rules += interactive_custom_rule_builder(debug)

    rules += confirm_policy_drop()

    if confirm_and_display_rules(rules):
        return rules
    else:
        print("Aborted.")
        return None

def main():
    config = load_config()
    host_alias = input("Host alias (as in config.json): ").strip()
    host_info = get_host_config(config, host_alias)

    if not host_info:
        print("Invalid host alias.")
        return

    rules = build_rules(debug=True)
    if not rules:
        return

    success, output = push_iptables_config(
        host=host_info["ip"],
        port=host_info.get("port", 22),
        username=host_info["user"],
        key_path=host_info["key"],
        iptables_commands=rules,
        debug=True
    )

    print("✅ Success" if success else "❌ Failed")
    print(output)

if __name__ == "__main__":
    main()
