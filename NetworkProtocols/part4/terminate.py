import os
import subprocess
import json

def find_pid(port):
    try:
        result = subprocess.run(
            ["lsof", "-t", "-i:{}".format(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.stdout:
            return result.stdout.strip()  # Return the PID as a string
        else:
            print(f"No process found on port {port}.")
            return None
            
    except Exception as e:
        print(f"Error while finding PID: {e}")
        return None

def kill_process(pid):
    try:
        os.kill(int(pid), 9)  # 9 is the signal for SIGKILL
        print(f"Process {pid} has been terminated.")
    except Exception as e:
        print(f"Error while killing process {pid}: {e}")

def get_port_from_config(config_file):
    try:
        with open(config_file, 'r') as file:
            config = json.load(file)
            return config.get("server_port")
    except Exception as e:
        print(f"Error reading config file: {e}")
        return None

if __name__ == "__main__":
    config_file = 'config.json'
    port = get_port_from_config(config_file)
    
    if port is not None:
        pid = find_pid(port)
        if pid:
            kill_process(pid)
    else:
        print("Port could not be retrieved from config.")
