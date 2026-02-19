import os
import sys
import subprocess
import json
import socket
import getpass 
import tkinter as tk
from tkinter import messagebox, simpledialog

class WorldXLauncher:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(self.base_dir)
        self.setup_environment()
        
        self.root = tk.Tk()
        self.root.title("WorldX - Multi-Server")
        self.root.geometry("400x550")
        self.root.configure(bg="#1a1a1a")

        tk.Label(self.root, text="WORLD X", font=("Courier", 35, "bold"), fg="#00ff00", bg="#1a1a1a").pack(pady=20)
        self.listbox = tk.Listbox(self.root, width=40, height=10, bg="#2d2d2d", fg="#00ff00", font=("Consolas", 12))
        self.listbox.pack(pady=10)

        tk.Button(self.root, text="REFRESH LIST", command=self.load_servers, width=25).pack(pady=5)
        tk.Button(self.root, text="CREATE SERVER", command=self.create_server, bg="#444", fg="white", width=25).pack(pady=5)
        tk.Button(self.root, text="JOIN WORLD", command=self.launch_game, bg="#007acc", fg="white", font=("Arial", 12, "bold"), width=25).pack(pady=20)

        self.load_servers()
        self.root.mainloop()

    def setup_environment(self):
        for folder in ['data', 'assets', 'servers']:
            if not os.path.exists(folder): os.makedirs(folder)
        
        for lib in ['ursina', 'websocket-client', 'websockets']:
            try:
                __import__(lib.replace('-', '_'))
            except ImportError:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

        server_file = 'data/servers.json'
        if not os.path.exists(server_file):
            with open(server_file, 'w') as f:
                json.dump([{"name": "Main Grass Field", "port": 8765}], f)

    def create_custom_server_script(self, name, port):
        safe_name = "".join(x for x in name if x.isalnum())
        file_path = f"servers/server_{safe_name}.py"
        server_code = f'''
import asyncio, websockets, json
clients = {{}} 
async def handler(websocket):
    player_id = None
    try:
        async for message in websocket:
            data = json.loads(message)
            player_id = data.get('id')
            clients[websocket] = player_id
            for client in list(clients.keys()):
                if client != websocket: await client.send(message)
    except: pass
    finally:
        if websocket in clients:
            pid = clients.pop(websocket)
            disconnect_msg = json.dumps({{"type": "disconnect", "id": pid}})
            for client in list(clients.keys()):
                try: await client.send(disconnect_msg)
                except: pass
async def main():
    async with websockets.serve(handler, "0.0.0.0", {port}): await asyncio.Future()
if __name__ == "__main__": asyncio.run(main())
'''
        with open(file_path, "w") as f: f.write(server_code.strip())
        return file_path

    def create_default_engine(self, path, port):
        os_user = getpass.getuser()
        engine_code = f'''
import sys, json, threading, random, atexit
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
try: import websocket
except: websocket = None

app = Ursina()
my_id = str(random.randint(1000, 9999))
my_name = "{os_user}"
window.title = f"WorldX ({{my_name}})"
window.exit_button.visible = False

ground = Entity(model='plane', scale=1000, texture='white_cube', texture_scale=(1000,1000), color=color.green, collider='box')
Sky()
player = FirstPersonController(speed=12)
other_players = {{}}
ws = None

# UI Elements
chat_input = InputField(max_lines=1, y=-.45, enabled=False)

def show_bubble(entity, message):
    b = Text(text=message, parent=entity, y=2.5, scale=12, billboard=True, background=True)
    destroy(b, delay=5)

def on_message(ws_conn, msg):
    try:
        data = json.loads(msg)
        p_id = data.get('id')
        if p_id == my_id: return
        
        if data.get('type') == 'disconnect':
            if p_id in other_players:
                destroy(other_players[p_id])
                del other_players[p_id]
            return

        if p_id not in other_players:
            other_players[p_id] = Entity(model='cube', color=color.orange, scale=(1,2,1))
            other_players[p_id].name_tag = Text(
                text=data.get('name', 'Player'), 
                parent=other_players[p_id], 
                y=1.2, 
                scale=10, 
                billboard=True, 
                color=color.yellow
            )
        
        if data['type'] == 'pos':
            other_players[p_id].position = Vec3(*data['pos'])
        elif data['type'] == 'chat':
            show_bubble(other_players[p_id], data['text'])
    except: pass

def network_loop():
    global ws
    try:
        ws = websocket.WebSocketApp("ws://localhost:{port}", on_message=on_message)
        ws.run_forever()
    except: pass

threading.Thread(target=network_loop, daemon=True).start()

def cleanup():
    if ws and ws.sock and ws.sock.connected:
        try:
            ws.send(json.dumps({{"type": "disconnect", "id": my_id}}))
            ws.close()
        except: pass

atexit.register(cleanup)
window.on_close = cleanup

def input(key):
    # Press 'C' to open chat
    if key == 'c':
        chat_input.enabled = not chat_input.enabled
        chat_input.active = chat_input.enabled
        player.enabled = not chat_input.enabled
        mouse.locked = not chat_input.enabled
    
    # Press Enter to send
    elif key == 'enter' and chat_input.enabled:
        if chat_input.text.strip():
            msg = {{"type": "chat", "id": my_id, "name": my_name, "text": chat_input.text}}
            if ws and ws.sock and ws.sock.connected: 
                ws.send(json.dumps(msg))
            show_bubble(player, chat_input.text)
        
        chat_input.text = ""
        chat_input.enabled = False
        player.enabled = True
        mouse.locked = True
    
    elif key == 'escape':
        cleanup()
        application.quit()

def update():
    if ws and ws.sock and ws.sock.connected:
        try: 
            ws.send(json.dumps({{"type": "pos", "id": my_id, "name": my_name, "pos": [player.x, player.y, player.z]}}))
        except: pass

app.run()
'''
        with open(path, "w") as f: f.write(engine_code.strip())

    def start_server_if_needed(self, name, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.settimeout(1)
            s.connect(("localhost", port))
            s.close()
        except:
            script_path = self.create_custom_server_script(name, port)
            subprocess.Popen([sys.executable, script_path], creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)

    def load_servers(self):
        self.listbox.delete(0, tk.END)
        try:
            if os.path.exists('data/servers.json'):
                with open('data/servers.json', 'r') as f:
                    self.server_data = json.load(f)
                    for s in self.server_data:
                        self.listbox.insert(tk.END, f"{s['name']} (Port: {s['port']})")
        except: pass

    def create_server(self):
        name = simpledialog.askstring("WorldX", "Server Name:")
        if name:
            new_port = self.server_data[-1]['port'] + 1 if self.server_data else 8765
            self.server_data.append({"name": name, "port": new_port})
            with open('data/servers.json', 'w') as f:
                json.dump(self.server_data, f, indent=4)
            self.load_servers()

    def launch_game(self):
        idx = self.listbox.curselection()
        if idx:
            server = self.server_data[idx[0]]
            self.start_server_if_needed(server['name'], server['port'])
            engine_path = os.path.join(self.base_dir, "game_engine.py")
            self.create_default_engine(engine_path, server['port'])
            subprocess.Popen([sys.executable, engine_path, server['name']])
            self.root.destroy()

if __name__ == "__main__":
    WorldXLauncher()