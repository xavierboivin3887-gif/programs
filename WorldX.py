import tkinter as tk
from tkinter import messagebox
import json
import os
import random
import subprocess
import shutil
from datetime import datetime

# --- CONFIGURATION ---
VIDEO_FOLDER = "worldx_tv"
GAME_FOLDER = "worldx_games"
TRASH_FOLDER = "worldx_trash"
SETTINGS_FILE = "settings.json"

# Approved Extensions
LEGAL_VIDEO = [".mp4"]
LEGAL_GAMES = [".py", ".exe", ".url", ".lnk"]

for folder in [VIDEO_FOLDER, GAME_FOLDER, TRASH_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

class WorldXApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WorldX - Official Hub")
        self.root.geometry("950x800") 
        self.root.configure(bg="#d9d9d9")
        
        # --- UNIVERSAL COMIC SANS ---
        self.font_name = "Comic Sans MS"
        self.font_main = (self.font_name, 12, "bold")
        self.font_header = (self.font_name, 26, "bold")
        self.font_list = (self.font_name, 11)
        self.font_small = (self.font_name, 9, "bold")
        
        self.neon_colors = ["#39FF14", "#FF007F", "#00FFFF", "#FFFF00", "#FF5F1F", "#BC13FE"]
        self.settings = self.load_settings()
        self.sort_newest = True
        
        self.main_container = tk.Frame(self.root, bg="#d9d9d9")
        self.main_container.pack(fill="both", expand=True)
        self.draw_hub()

    def load_settings(self):
        # --- EXPANDED ACHIEVEMENTS LIST ---
        # The list is defined here, but the display will reverse it so the bottom ones appear on top
        default_achievements = {
            "GAMES!!!": False,
            "TV!!!": False,
            "I'M A GOOFY GOOBER": False,
            "YOU'RE UNDER ARREST FOR TRAFFICKING ILLEGAL FILES!!!": False,
            "NOOB!!!": False,
            "GARBAGE DAY!!!": False,
            "IT'S ALIVE!!!": False,
            "BYE BYE!!!": False,
            "STALKER!!!": False,
            "ARE YOU LOST???": False,
            "COVERING YOUR TRACKS!!!": False,
            "SORT IT OUT!!!": False,
            "DOUBLE CLICK!!!": False
        }

        if not os.path.exists(SETTINGS_FILE):
            default = {
                "tutorial_completed": False, 
                "history": [],
                "achievements": default_achievements
            }
            with open(SETTINGS_FILE, "w") as f: json.dump(default, f, indent=4)
            return default
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                if "history" not in data: data["history"] = []
                # Merge new achievements if they don't exist in old save file
                if "achievements" not in data: data["achievements"] = {}
                for k, v in default_achievements.items():
                    if k not in data["achievements"]:
                        data["achievements"][k] = v
                return data
        except: return {"tutorial_completed": False, "history": [], "achievements": default_achievements}

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as f: json.dump(self.settings, f, indent=4)

    def add_to_history(self, action):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.settings["history"].append(f"[{now}] {action}")
        self.save_settings()

    def unlock_achievement(self, name):
        if self.settings.get("achievements") and not self.settings["achievements"].get(name):
            self.settings["achievements"][name] = True
            self.add_to_history(f"ACHIEVEMENT UNLOCKED: {name}")
            self.save_settings()
            messagebox.showinfo("ACHIEVEMENT UNLOCKED!", f"🏆 {name}")

    def check_for_contraband(self, folder, allowed_exts):
        """Scans for illegal files. If found, asks the user to move them to Quarantine."""
        all_files = os.listdir(folder)
        for f in list(all_files):
            ext = os.path.splitext(f)[1].lower()
            if ext not in allowed_exts:
                self.unlock_achievement("YOU'RE UNDER ARREST FOR TRAFFICKING ILLEGAL FILES!!!")
                
                msg = (f"SECURITY ALERT!\n\nThe file '{f}' is ILLEGAL in this section.\n"
                       "Do you want to move it to Quarantine?")
                
                if messagebox.askyesno("ILLEGAL FILE DETECTED", msg):
                    try:
                        src = os.path.join(folder, f)
                        dst = os.path.join(TRASH_FOLDER, f)
                        if os.path.exists(dst):
                            base, extension = os.path.splitext(f)
                            timestamp = datetime.now().strftime("%H%M%S")
                            dst = os.path.join(TRASH_FOLDER, f"{base}_{timestamp}{extension}")
                        shutil.move(src, dst)
                        self.add_to_history(f"Quarantined illegal file: {f}")
                        messagebox.showinfo("SUCCESS", f"File '{f}' has been quarantined.")
                    except Exception as e:
                        messagebox.showerror("ERROR", f"Could not move file: {e}")

    # --- STATIONS ---
    def draw_tv(self):
        self.unlock_achievement("TV!!!")
        self.add_to_history("Accessed TV Station")
        self.check_for_contraband(VIDEO_FOLDER, LEGAL_VIDEO)
        for w in self.content_area.winfo_children(): w.destroy()
        tk.Label(self.content_area, text="TV STATION", font=self.font_header, fg="red", bg="#d9d9d9").pack()
        files = [f for f in os.listdir(VIDEO_FOLDER) if f.lower().endswith(".mp4")]
        self.create_grid(files, "TV", lambda x: os.startfile(os.path.join(VIDEO_FOLDER, x)))

    def draw_games(self):
        self.unlock_achievement("GAMES!!!")
        self.add_to_history("Accessed Game Station")
        self.check_for_contraband(GAME_FOLDER, LEGAL_GAMES)
        for w in self.content_area.winfo_children(): w.destroy()
        tk.Label(self.content_area, text="GAME STATION", font=self.font_header, fg="green", bg="#d9d9d9").pack()
        files = [f for f in os.listdir(GAME_FOLDER) if f.lower().endswith(tuple(LEGAL_GAMES))]
        self.create_grid(files, "PLAY", self.run_game)

    # --- HISTORY SECTION ---
    def draw_history(self):
        self.unlock_achievement("STALKER!!!")
        for w in self.content_area.winfo_children(): w.destroy()
        tk.Label(self.content_area, text="HISTORY", font=self.font_header, bg="#d9d9d9", fg="#444444").pack(pady=10)
        list_frame = tk.Frame(self.content_area, bg="white", relief="sunken", borderwidth=2)
        list_frame.pack(fill="both", expand=True, padx=40, pady=10)
        lb = tk.Listbox(list_frame, font=self.font_list, bg="white", borderwidth=0)
        lb.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(list_frame); sb.pack(side="right", fill="y")
        lb.config(yscrollcommand=sb.set); sb.config(command=lb.yview)
        # Reverse History (Newest on top)
        for entry in reversed(self.settings.get("history", [])): lb.insert(tk.END, entry)
        tk.Button(self.content_area, text="CLEAR HISTORY", bg="#808080", fg="white", font=self.font_small, command=self.clear_history_data).pack(pady=10)

    def clear_history_data(self):
        if messagebox.askyesno("WorldX", "Clear all history logs?"):
            self.settings["history"] = []
            self.unlock_achievement("COVERING YOUR TRACKS!!!")
            self.save_settings(); self.draw_history()

    # --- QUARANTINE MANAGER ---
    def draw_quarantine(self):
        self.add_to_history("Opened Quarantine Manager")
        for w in self.content_area.winfo_children(): w.destroy()
        tk.Label(self.content_area, text="QUARANTINE MANAGER", font=self.font_header, fg="#ffaa00", bg="#d9d9d9").pack(pady=10)
        ctrl_f = tk.Frame(self.content_area, bg="#d9d9d9"); ctrl_f.pack(fill="x", padx=40, pady=5)
        tk.Label(ctrl_f, text="SEARCH:", font=self.font_small, bg="#d9d9d9").pack(side="left")
        self.q_search = tk.Entry(ctrl_f, font=self.font_list); self.q_search.pack(side="left", fill="x", expand=True, padx=5)
        self.q_search.bind("<KeyRelease>", self.filter_quarantine)
        self.sort_btn = tk.Button(ctrl_f, text="SORT: NEWEST", bg="#808080", fg="white", font=self.font_small, command=self.toggle_sort); self.sort_btn.pack(side="left", padx=5)
        list_frame = tk.Frame(self.content_area, bg="white", relief="sunken", borderwidth=2); list_frame.pack(fill="both", expand=True, padx=40, pady=10)
        self.trash_list = tk.Listbox(list_frame, font=self.font_list, bg="white", borderwidth=0); self.trash_list.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(list_frame); sb.pack(side="right", fill="y"); self.trash_list.config(yscrollcommand=sb.set); sb.config(command=self.trash_list.yview)
        self.update_q_list()
        btn_frame = tk.Frame(self.content_area, bg="#d9d9d9"); btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="DELETE SELECTED", bg="#ff5555", fg="white", font=self.font_small, command=self.delete_single_file).pack(side="left", padx=5)
        tk.Button(btn_frame, text="EMPTY TRASH", bg="red", fg="white", font=self.font_small, command=self.empty_trash).pack(side="left", padx=5)
        tk.Button(btn_frame, text="RESTORE SELECTED", bg="blue", fg="white", font=self.font_small, command=self.restore_file).pack(side="left", padx=5)
        tk.Button(btn_frame, text="RESTORE ALL", bg="#00aa00", fg="white", font=self.font_small, command=self.restore_all).pack(side="left", padx=5)

    def update_q_list(self, filter_text=""):
        self.trash_list.delete(0, tk.END)
        files = [(f, os.path.getmtime(os.path.join(TRASH_FOLDER, f))) for f in os.listdir(TRASH_FOLDER)]
        if self.sort_newest: files.sort(key=lambda x: x[1], reverse=True)
        else: files.sort(key=lambda x: x[0].lower())
        for f, t in files:
            if filter_text.lower() in f.lower(): self.trash_list.insert(tk.END, f)
        self.sort_btn.config(text="SORT: NEWEST" if self.sort_newest else "SORT: A-Z")

    def toggle_sort(self): 
        self.sort_newest = not self.sort_newest
        self.unlock_achievement("SORT IT OUT!!!")
        self.update_q_list(self.q_search.get())
        
    def filter_quarantine(self, event): self.update_q_list(self.q_search.get())
    
    def delete_single_file(self):
        try:
            sel = self.trash_list.get(self.trash_list.curselection())
            if messagebox.askyesno("WorldX", f"Delete {sel} forever?"):
                os.remove(os.path.join(TRASH_FOLDER, sel))
                self.unlock_achievement("BYE BYE!!!")
                self.add_to_history(f"Deleted forever: {sel}")
                self.draw_quarantine()
        except: pass

    def empty_trash(self):
        if messagebox.askyesno("WorldX", "Wipe all Quarantine files?"):
            for f in os.listdir(TRASH_FOLDER): os.remove(os.path.join(TRASH_FOLDER, f))
            self.unlock_achievement("GARBAGE DAY!!!")
            self.add_to_history("Emptied Quarantine Trash"); self.draw_quarantine()

    def restore_file(self):
        try:
            sel = self.trash_list.get(self.trash_list.curselection())
            dst = VIDEO_FOLDER if sel.lower().endswith(".mp4") else GAME_FOLDER
            shutil.move(os.path.join(TRASH_FOLDER, sel), os.path.join(dst, sel))
            self.unlock_achievement("IT'S ALIVE!!!")
            self.unlock_achievement("DOUBLE CLICK!!!")
            self.add_to_history(f"Restored: {sel}"); self.draw_quarantine()
        except: pass

    def restore_all(self):
        for f in os.listdir(TRASH_FOLDER):
            src, dest = os.path.join(TRASH_FOLDER, f), (VIDEO_FOLDER if f.lower().endswith(".mp4") else GAME_FOLDER)
            shutil.move(src, os.path.join(dest, f))
        self.unlock_achievement("IT'S ALIVE!!!")
        self.add_to_history("Restored all quarantined files"); self.draw_quarantine()

    # --- NAVIGATION ---
    def draw_hub(self):
        nav_bg = "#0055ff"
        top_nav = tk.Frame(self.main_container, bg=nav_bg, relief="raised", borderwidth=4)
        top_nav.pack(side="top", fill="x")
        btn_f = tk.Frame(top_nav, bg=nav_bg); btn_f.pack(fill="x", padx=10, pady=5)
        tk.Button(btn_f, text="GAME STATION", bg="#00aa00", fg="white", font=self.font_main, command=self.draw_games).pack(side="left", padx=5)
        tk.Button(btn_f, text="TV STATION", bg="#ff0000", fg="white", font=self.font_main, command=self.draw_tv).pack(side="left", padx=5)
        tk.Button(btn_f, text="QUARANTINE", bg="#ffaa00", font=self.font_main, command=self.draw_quarantine).pack(side="left", padx=5)
        tk.Button(btn_f, text="ACHIEVEMENTS", bg="#BC13FE", fg="white", font=self.font_main, command=self.draw_achievements).pack(side="left", padx=5)
        tk.Button(btn_f, text="HISTORY", bg="#808080", fg="white", font=self.font_main, command=self.draw_history).pack(side="left", padx=5)

        addr_f = tk.Frame(top_nav, bg=nav_bg); addr_f.pack(fill="x", padx=10, pady=5)
        tk.Label(addr_f, text="ADDRESS:", bg=nav_bg, fg="white", font=self.font_small).pack(side="left")
        self.addr = tk.Entry(addr_f, font=self.font_list); self.addr.pack(side="left", fill="x", expand=True, padx=5)
        self.addr.bind("<Return>", self.handle_addr)
        tk.Button(addr_f, text="GO", bg="#ffff00", font=self.font_small, command=self.handle_addr).pack(side="left")

        self.content_area = tk.Frame(self.main_container, bg="#d9d9d9"); self.content_area.pack(fill="both", expand=True)
        tk.Label(self.content_area, text="WORLDX HUB", font=self.font_header, bg="#d9d9d9", fg="#0055ff").pack(pady=100)
        if not self.settings.get("tutorial_completed", False): self.show_tutorial()

    def handle_addr(self, e=None):
        cmd = self.addr.get().upper().strip()
        if cmd in ["TUTORIAL", "TUT"]: 
            self.unlock_achievement("NOOB!!!")
            self.show_tutorial()
        elif cmd == "CREDITS":
            self.unlock_achievement("I'M A GOOFY GOOBER")
            messagebox.showinfo("CREDITS", "WorldX Created by goofygoober1942")
        else:
            self.unlock_achievement("ARE YOU LOST???")
        
        self.addr.delete(0, tk.END)

    def draw_achievements(self):
        self.add_to_history("Checked Achievement Board")
        for w in self.content_area.winfo_children(): w.destroy()
        
        # Header
        tk.Label(self.content_area, text="ACHIEVEMENTS", font=self.font_header, fg="#BC13FE", bg="#d9d9d9").pack(pady=10)
        
        # Listbox Frame (Exactly like History)
        list_frame = tk.Frame(self.content_area, bg="white", relief="sunken", borderwidth=2)
        list_frame.pack(fill="both", expand=True, padx=40, pady=10)
        
        lb = tk.Listbox(list_frame, font=self.font_list, bg="white", borderwidth=0)
        lb.pack(side="left", fill="both", expand=True)
        
        sb = tk.Scrollbar(list_frame)
        sb.pack(side="right", fill="y")
        
        lb.config(yscrollcommand=sb.set)
        sb.config(command=lb.yview)
        
        # Get Dictionary items
        ach_list = list(self.settings.get("achievements", {}).items())
        
        # REVERSE ORDER (Like History: Newest defined stuff at the top)
        for i, (name, unlocked) in enumerate(reversed(ach_list)):
            status = " [UNLOCKED]" if unlocked else " [LOCKED]"
            display_text = f"{name}{status}"
            lb.insert(tk.END, display_text)
            
            # Keep the Green/Gray color coding
            color = "#00aa00" if unlocked else "#555555"
            lb.itemconfigure(i, fg=color)

    def run_game(self, gm):
        self.add_to_history(f"Launched Game: {gm}")
        path = os.path.join(GAME_FOLDER, gm)
        if gm.lower().endswith(".py"): subprocess.Popen(["python", path], shell=True)
        else: os.startfile(path)

    def show_tutorial(self):
        self.add_to_history("Started Tutorial")
        self.tut_overlay = tk.Frame(self.main_container, bg="#0055ff", relief="raised", borderwidth=8)
        self.tut_overlay.place(relx=0.5, rely=0.5, anchor="center", width=550, height=450)
        self.tut_title = tk.Label(self.tut_overlay, text="", font=(self.font_name, 14, "bold"), bg="#0055ff", fg="#ffff00"); self.tut_title.pack(pady=10)
        self.tut_text = tk.Label(self.tut_overlay, text="", font=self.font_main, bg="#0055ff", fg="white", wraplength=480, justify="center"); self.tut_text.pack(expand=True, padx=20)
        self.stages = [
            {"title": "STAGE 1: How to use sections", "text": "Hey, you see the little blue box on top? Do you see the game section and the TV section button right next to each other in the top left corner? Yeah, go and click it. If you do click it, it will bring you to that section :)"},
            {"title": "STAGE 2: How to import videos to the TV section", "text": "First, get out of the app. Once you're out of the app, you should see worldx_tv. Now open that folder. Alright, now you're in. So, in here, you just have to port in any video you want, but remember, it has to be a MP4, or else it will give you an error message in the app saying what file is causing this error."},
            {"title": "STAGE 3: How to import games to the Game section", "text": "First, get out of the app. Once you're out of the app, you should see worldx_games. Now open that folder. Alright, now you're in. So, in here, you just have to port in any game you want, but remember, it has to be a .py, a .exe, a .url, or a .lnk shortcut, or else it will give you an error message in the app saying what file is causing this error."},
            {"title": "STAGE 4: How to use the address bar", "text": "In order to use the address bar, all you have to do is click on the address bar and then type in GAME or TV, and whatever number, Remember, your titles have to have a number on it or else the scanner will get confused and scan nothing. And the other important thing, you have to do TV or GAME space. What I mean is this TV 1942."},
            {"title": "STAGE DONE: How to finish the tutorial", "text": "All right, you finished the tutorial :)"}
        ]
        self.curr_idx = 0; self.update_tut()
        bf = tk.Frame(self.tut_overlay, bg="#0055ff"); bf.pack(side="bottom", fill="x", pady=20)
        self.tut_btn = tk.Button(bf, text="NEXT", bg="#ffff00", font=self.font_main, command=self.next_stage); self.tut_btn.pack(side="right", padx=20)
        tk.Button(bf, text="SKIP", bg="#808080", fg="white", font=self.font_main, command=self.finish_tutorial).pack(side="left", padx=20)

    def update_tut(self):
        s = self.stages[self.curr_idx]; self.tut_title.config(text=s["title"]); self.tut_text.config(text=s["text"])
        if self.curr_idx == len(self.stages)-1: self.tut_btn.config(text="FINISH", bg="#39FF14")
    def next_stage(self):
        if self.curr_idx < len(self.stages)-1: self.curr_idx += 1; self.update_tut()
        else: self.finish_tutorial()
    def finish_tutorial(self): 
        self.settings["tutorial_completed"] = True; self.save_settings(); self.tut_overlay.destroy(); self.add_to_history("Finished Tutorial")

    def create_grid(self, files, btn_text, action):
        grid = tk.Frame(self.content_area, bg="#f0f0f0"); grid.pack(fill="both", expand=True, padx=20)
        for i, f in enumerate(files):
            card = tk.Frame(grid, bg="#d9d9d9", width=200, height=160, relief="raised", borderwidth=3)
            card.grid(row=i//3, column=i%3, padx=15, pady=15); card.pack_propagate(0)
            tk.Button(card, text=btn_text, bg=random.choice(self.neon_colors), font=(self.font_name, 16, "bold"), command=lambda x=f: action(x)).pack(fill="both", expand=True)
            tk.Label(card, text=f, font=self.font_small, bg="#d9d9d9").pack()

if __name__ == "__main__":
    r = tk.Tk(); app = WorldXApp(r); r.mainloop()