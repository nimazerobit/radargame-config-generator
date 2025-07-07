import requests
from ping3 import ping
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import Application
from prompt_toolkit.widgets import MenuContainer, MenuItem
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.formatted_text import HTML
import easygui
import random
import string
import os
import platform

API_BASE = "https://api.radar.game/v1"

console = Console()

# Utils Functions
def log_success(msg): console.print(f"[green][OK][/green] {msg}")
def log_error(msg): console.print(f"[red][X][/red] {msg}")
def log_info(msg): console.print(f"[cyan][!][/cyan] {msg}")
def clear_console():
    os.system("cls" if platform.system() == "Windows" else "clear")
def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# Get auth token by passing username and password into this function
def get_token(username, password):
    try:
        response = requests.post(f"{API_BASE}/auth/login", json={"username": username, "password": password})
        data = response.json()
        if not data["isSuccess"]:
            log_error(data["message"])
            return None
        token = data["result"]["accessToken"]
        log_success("Logged in successfully.")
        return token
    except Exception as e:
        log_error(f"Login failed: {e}")
        return None

# Get server list and return them
def get_servers(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/user/servers", headers=headers)
        data = response.json()
        if not data["isSuccess"]:
            log_error(data["message"])
            return []
        return data["result"]
    except Exception as e:
        log_error(f"Failed to fetch servers: {e}")
        return []

# Ping server by passing ip into this function
def ping_server(ip):
    try:
        ip = ip.split(":")[0]
        latency = ping(ip, timeout=1)
        return round(latency * 1000) if latency else None
    except:
        return None

# Draw server selection menu
def draw_menu(servers):
    from prompt_toolkit.shortcuts import radiolist_dialog

    choices = []
    for server in servers:
        location = server.get("location", "Unknown")
        endpoint = server.get("ipPublic") or "N/A"
        load = server.get("loadPercentage") or 0
        latency = ping_server(endpoint)
        ping_text = f"{latency} ms" if latency else "timeout"
        label = f"{location} - {endpoint} | Load: {load}% | Ping: {ping_text}"
        choices.append((server["id"], label))

    result = radiolist_dialog(
        title="Choose Server",
        text="Select a server:\nYou can use your mouse too.",
        values=choices,
    ).run()

    return result

# Get config by passing auth token and server id to this function
def get_config(token, server_id):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{API_BASE}/user/account/getAccount", headers=headers, params={"serverId": server_id})
        data = response.json()
        if not data["isSuccess"]:
            log_error(data["message"])
            return None
        return data["result"]
    except Exception as e:
        log_error(f"Failed to generate config: {e}")
        return None

# Generate valid WireGuard config from api data and open file save window for user
def save_config_file(config_data):
    try:
        rand = generate_random_string()
        default_name = f"radar-{rand}.conf"
        file_path = easygui.filesavebox(title="Save Config", default=default_name, filetypes=["*.conf"])
        if file_path:
            header_notes = (
                f"# Radar WireGuard Config\n"
                f"# Telegram : @nimazerobit\n"
                f"# !!! Just 1 device can connect to this config !!!\n"
                f"# Use this with the official WireGuard app.\n\n"
            )
            content = header_notes + f"""[Interface]
PrivateKey = {config_data['privateKey']}
Address = {config_data['addresses']}
DNS = {"8.8.8.8, 1.1.1.1"}
MTU = {config_data['mtu']}

[Peer]
PublicKey = {config_data['endpointPublicKey']}
PresharedKey = {config_data['presharedKey']}
Endpoint = {config_data['endpoint']}
AllowedIPs = {config_data['allowedIPs']}
PersistentKeepalive = {config_data['persistentKeepalive']}
"""
            with open(file_path, "w") as f:
                f.write(content)
            log_success(f"Config saved to: {file_path}")
        else:
            log_info("Save cancelled.")
    except Exception as e:
        log_error(f"Failed to save config: {e}")

def main():
    clear_console()
    console.rule("[bold blue]Radar Game Config Generator[/bold blue]")
    console.rule("@nimazerobit\n")

    print("\n")

    log_info("Register an account on https://radar.game/register and verify your email.")
    log_info("The password will not be shown while typing for security reasons.")
    log_info("If you encounter any issues, contact @nimazerobit on Telegram.")

    print("\n")

    username = Prompt.ask("Enter Radar username/email")
    password = Prompt.ask("Enter password", password=True)
    

    token = get_token(username, password)
    if not token:
        return
    
    log_info("Loading Servers Please Wait...")

    servers = get_servers(token)
    if not servers:
        return

    selected_id = draw_menu(servers)
    if not selected_id:
        log_info("No server selected.")
        return

    config = get_config(token, selected_id)
    if not config:
        return

    save_config_file(config, username)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Exited.[/bold red]")
