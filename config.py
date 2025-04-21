import json
import os

def load_config(path='config.json'):
    if not os.path.exists(path):
        print("[WARN] No config.json found.")
        return {}
    with open(path, 'r') as f:
        return json.load(f)

def get_host_config(config, host_alias):
    return config.get("hosts", {}).get(host_alias, {})
