import paramiko

def push_iptables_config(host, port, username, key_path, iptables_commands, debug=False):
    try:
        key = paramiko.RSAKey.from_private_key_file(key_path)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, port=port, username=username, pkey=key)

        full_output = ""
        for cmd in iptables_commands:
            if debug:
                print("[DEBUG] Executing:", cmd)
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode()
            err = stderr.read().decode()
            full_output += f"\n$ {cmd}\n{out}{err}"
            if stderr.channel.recv_exit_status() != 0:
                client.close()
                return False, f"Failed on command: {cmd}\n{err}"

        save_cmd = "iptables-save > /etc/iptables/rules.v4"
        if debug:
            print("[DEBUG] Executing:", save_cmd)
        stdin, stdout, stderr = client.exec_command(save_cmd)
        out = stdout.read().decode()
        err = stderr.read().decode()
        if stderr.channel.recv_exit_status() != 0:
            client.close()
            return False, f"Failed to save iptables rules.\n{err}"

        client.close()
        return True, full_output

    except Exception as e:
        return False, str(e)
