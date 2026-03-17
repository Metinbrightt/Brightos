import os, json, time, math, random, threading
import tkinter as tk
from tkinter import messagebox
from collections import deque
import sys
from pathlib import Path

def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent

BASE_DIR        = get_base_dir()
VAULT_DIR       = BASE_DIR / "security_vault"
API_FILE        = VAULT_DIR / "access.json"

SYSTEM_NAME     = "BRIGHTOS — NEURAL ARCHIVE"
MODEL_BADGE     = "AUTHENTIC ARTIFICIAL INTELLIGENCE CORE"

# THEME: DEEP SPACE JARVIS
C_BG      = "#010101"  # Pure Void
C_PRIMARY = "#00f2ff"  # Kinetic Cyan
C_SECONDARY = "#005a72" # Deep Slate Cyan
C_GLOW    = "#002a35"  # Faint Glow
C_TEXT    = "#f0f8ff"  # Ghost White
C_ALERT   = "#ff0055"  # System Alert Red

class BrightOSUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{SYSTEM_NAME}")
        self.root.resizable(False, False)
        
        # Larger Screen
        W, H = 1200, 900
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{W}x{H}+{(sw-W)//2}+{(sh-H)//2}")
        self.root.configure(bg=C_BG)

        self.W, self.H = W, H
        self.tick = 0
        self.speaking = False
        self.status_text = "HYPER-THREADING ACTIVE"
        self.typing_queue = deque()
        self.is_typing = False
        
        # Sensory State
        self.visual_status = "AWARE"
        self.health_status = "STABLE"
        self.alert_text    = ""
        self.alert_timer   = 0

        self.canvas = tk.Canvas(self.root, width=W, height=H, bg=C_BG, highlightthickness=0)
        self.canvas.place(x=0, y=0)

        # Kinetic Terminal
        self.log_frame = tk.Frame(self.root, bg="#05080a", highlightbackground=C_PRIMARY, highlightthickness=1)
        self.log_text = tk.Text(self.log_frame, bg="#05080a", fg=C_PRIMARY, font=("Consolas", 11), borderwidth=0, padx=15, pady=12)
        self.log_text.pack(fill="both", expand=True)
        self.log_text.configure(state="disabled")

        self._api_key_ready = False
        if API_FILE.exists():
            try:
                with open(API_FILE, "r") as f:
                    data = json.load(f)
                    if data.get("gemini_api_key"):
                        self._api_key_ready = True
            except: pass

        if not self._api_key_ready:
            self.root.withdraw() 
            self._show_setup_ui()
        else:
            self._start_engine()

    def _start_engine(self):
        self.root.deiconify()
        self._animate()
        self.root.protocol("WM_DELETE_WINDOW", lambda: os._exit(0))

    def _animate(self):
        self.tick += 1
        self._draw()
        self.root.after(30, self._animate)

    def _draw(self):
        c = self.canvas
        c.delete("all")

        cx, cy = self.W // 2, self.H // 2 - 80
        t = self.tick

        # 1. Background Grid & Particles
        for i in range(0, self.W, 60):
            c.create_line(i, 0, i, self.H, fill="#04080a", width=1)
        for i in range(0, self.H, 60):
            c.create_line(0, i, self.W, i, fill="#04080a", width=1)

        # 2. JARVIS KINETIC CORE (The Rings)
        # Ring 1 (External - Slow reverse)
        r1 = 280
        c.create_oval(cx-r1, cy-r1, cx+r1, cy+r1, outline=C_SECONDARY, width=1, dash=(5, 15))
        self._draw_arc_ring(cx, cy, r1, t * -0.5, 40, C_PRIMARY, 2)

        # Ring 2 (Middle - Pulsing)
        pulse = math.sin(t * 0.1) * 10
        r2 = 220 + pulse
        c.create_oval(cx-r2, cy-r2, cx+r2, cy+r2, outline=C_GLOW, width=8)
        self._draw_arc_ring(cx, cy, r2, t * 1.2, 120, C_PRIMARY, 3)

        # Ring 3 (Data Ring)
        r3 = 180
        for i in range(0, 360, 45):
            ang = math.radians(i + t)
            x = cx + r3 * math.cos(ang)
            y = cy + r3 * math.sin(ang)
            c.create_text(x, y, text=random.choice(["0", "1"]), fill=C_SECONDARY, font=("Consolas", 8))

        # Ring 4 (Internal Core)
        r4 = 140
        c.create_oval(cx-r4, cy-r4, cx+r4, cy+r4, outline=C_PRIMARY, width=2)
        
        # Audio Visualizer Circle
        for i in range(0, 360, 10):
            ang = math.radians(i)
            base_h = 15
            wave = random.randint(5, 50) if self.speaking else (base_h + math.sin(t*0.2 + i)*10)
            x1 = cx + (r4-5) * math.cos(ang)
            y1 = cy + (r4-5) * math.sin(ang)
            x2 = cx + (r4-5-wave) * math.cos(ang)
            y2 = cy + (r4-5-wave) * math.sin(ang)
            c.create_line(x1, y1, x2, y2, fill=C_PRIMARY if wave < 35 else C_ALERT, width=3)

        # 3. HUD Elements (Top Corners)
        c.create_text(50, 40, text="◈ BRIGHTOS — NEURAL CORE v4.0", fill=C_PRIMARY, font=("Verdana", 12, "bold"), anchor="w")
        c.create_text(self.W-50, 40, text=time.strftime("%H:%M:%S"), fill=C_PRIMARY, font=("Consolas", 14), anchor="e")
        
        # 4. SENSORY HUD (Left Side)
        c.create_rectangle(40, 100, 200, 200, outline=C_SECONDARY, width=1)
        c.create_text(50, 115, text="SENSORY HUB", fill=C_SECONDARY, font=("Consolas", 8, "bold"), anchor="w")
        c.create_text(50, 140, text=f"• VISION: {self.visual_status}", fill=C_PRIMARY if self.visual_status == "AWARE" else C_ALERT, font=("Consolas", 8), anchor="w")
        c.create_text(50, 160, text=f"• HEALTH: {self.health_status}", fill=C_PRIMARY, font=("Consolas", 8), anchor="w")
        c.create_text(50, 180, text=f"• OPS: AUTONOMOUS", fill=C_PRIMARY, font=("Consolas", 8), anchor="w")

        # 5. PROACTIVE ALERT BANNER
        if self.alert_text:
            alpha = (math.sin(t*0.2)+1)/2
            c.create_rectangle(0, 0, self.W, 30, fill="#300010", outline=C_ALERT)
            c.create_text(cx, 15, text=f"⚠ PROACTIVE ALERT: {self.alert_text}", fill=C_ALERT, font=("Verdana", 9, "bold"))

        # Central HUD lines
        c.create_line(cx-400, 70, cx-100, 70, fill=C_SECONDARY)
        c.create_line(cx+100, 70, cx+400, 70, fill=C_SECONDARY)
        c.create_text(cx, 70, text="NEURAL LINK: ESTABLISHED", fill=C_TEXT, font=("Consolas", 8))

        # Bottom HUD Info
        c.create_text(cx, 650, text=f"INTERFACE STATE: {self.status_text}", fill=C_PRIMARY, font=("Consolas", 10, "bold"))
        c.create_text(cx, 675, text="OPERATOR MODE: ENGAGED", fill=C_SECONDARY, font=("Consolas", 8))

    def _draw_arc_ring(self, cx, cy, r, start_ang, extent, color, width):
        # Arcs for a complex kinetic look
        self.canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=start_ang, extent=extent, outline=color, style="arc", width=width)
        self.canvas.create_arc(cx-r, cy-r, cx+r, cy+r, start=start_ang+180, extent=extent, outline=color, style="arc", width=width)

    def write_log(self, text: str):
        self.typing_queue.append(text)
        if not self.is_typing: self._start_typing()

    def _start_typing(self):
        if not self.typing_queue: self.is_typing = False; return
        self.is_typing = True
        line = self.typing_queue.popleft()
        
        # Professional formatting
        prefix = "»"
        if "You:" in line: line = line.replace("You:", "[USER] "); prefix = "◈"
        if "Jarvis:" in line: line = line.replace("Jarvis:", "[NEURAL] "); prefix = "❖"
        if "SYS:" in line: line = line.replace("SYS:", "[SYSTEM] "); prefix = "⚠"
        
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"\n{prefix} {line}")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")
        self.root.after(10, self._start_typing)

    def request_new_key(self, message="INVALID KEY DETECTED"):
        self._api_key_ready = False
        self.root.after(0, lambda: self._show_setup_ui(message))

    def _show_setup_ui(self, custom_msg=None):
        win = tk.Toplevel()
        win.title("SYSTEM AUTHORIZATION REQUIRED")
        win.geometry("500x320")
        win.configure(bg=C_BG)
        win.resizable(False, False)
        win.attributes("-topmost", True)
        
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        win.geometry(f"500x320+{(sw-500)//2}+{(sh-320)//2}")

        tk.Label(win, text="◈ BRIGHTOS NEURAL IGNITION", fg=C_PRIMARY, bg=C_BG, font=("Verdana", 14, "bold")).pack(pady=20)
        
        if custom_msg:
            tk.Label(win, text=custom_msg, fg=C_ALERT, bg=C_BG, font=("Consolas", 10, "bold")).pack()
            
        tk.Label(win, text="SECURE API MASTER KEY REQUIRED", fg=C_TEXT, bg=C_BG, font=("Consolas", 9)).pack(pady=5)
        
        e = tk.Entry(win, width=40, show="*", bg="#05080a", fg=C_PRIMARY, insertbackground=C_PRIMARY, font=("Consolas", 10))
        e.pack(pady=10)
        e.focus_set()

        def save(evt=None):
            key = e.get().strip()
            if key:
                try:
                    current_data = {}
                    if API_FILE.exists():
                        try:
                            with open(API_FILE, "r") as f: current_data = json.load(f)
                        except: pass
                    current_data["gemini_api_key"] = key
                    VAULT_DIR.mkdir(parents=True, exist_ok=True)
                    with open(API_FILE, "w") as f: json.dump(current_data, f)
                    win.destroy()
                    self._api_key_ready = True
                    self._start_engine()
                except Exception as ex:
                    messagebox.showerror("VAULT ERROR", f"Security breach writing to vault: {ex}")

        btn = tk.Button(win, text="[ AUTHORIZE CORE ]", command=save, bg="#0a1014", fg=C_PRIMARY, 
                        activebackground=C_PRIMARY, activeforeground=C_BG, borderwidth=1, relief="flat", padx=20, pady=10)
        btn.pack(pady=20)
        win.bind("<Return>", save)
        win.protocol("WM_DELETE_WINDOW", lambda: os._exit(0))

    def start_speaking(self): self.speaking = True; self.status_text = "HYPER-STREAM DATA INJECT"
    def stop_speaking(self): self.speaking = False; self.status_text = "READY FOR SIGNAL"

    def show_proactive_alert(self, text: str):
        self.alert_text = text
        self.root.after(5000, lambda: setattr(self, "alert_text", ""))

    def update_sensory(self, vision="AWARE", health="STABLE"):
        self.visual_status = vision
        self.health_status = health

    def wait_for_api_key(self):
        while not self._api_key_ready: time.sleep(0.1)

if __name__ == "__main__":
    ui = BrightOSUI()
    ui.root.mainloop()
