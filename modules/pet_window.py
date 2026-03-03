"""
pet_window.py - Premium desktop pet UI (LumiLog 灵犀笔记)
Approach: tkinter shell (transparent window) + embedded tkinter canvas
with programmatic pixel-art sprite rendering and smooth animation engine.

Design philosophy inspired by VPet/Steam desktop pets:
- Real sprite-based animation (not emoji)
- Particle effects for interactions
- Smooth floating/breathing motion
- Rich panel UI with glassmorphism aesthetic
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import math
import time
import random
from datetime import datetime
from typing import Callable

# ── Color palette (Dark Cyber / Neon Glassmorphism) ─────────────────────────
C = {
    "bg":        "#09090b",   # Deep space black
    "panel":     "#0f111a",   # Dark tech grey
    "card":      "#131521",
    "card2":     "#181a29",
    "accent":    "#22d3ee",   # Neon Cyan
    "accent2":   "#a855f7",   # Electric Purple
    "glow":      "#818cf8",   # Indigo glow
    "text":      "#f8fafc",   # Crisp white
    "muted":     "#64748b",
    "success":   "#10b981",
    "warn":      "#f59e0b",
    "error":     "#ef4444",
    # Holo-Fox specific
    "holo_outline": "#38bdf8", # Light blue wireframe
    "holo_core":    "#1e1b4b", # Dark purple inner core
    "holo_eye":     "#67e8f9", # Glowing cyan eyes
}

# ── Typography (Premium thin sans-serif & monospace) ───────────────────────
# Try Segoe UI Variable Display for that Windows 11 sleekness, fallback to Segoe UI
FONT     = ("Segoe UI Variable Display", 9)
FONT_SM  = ("Segoe UI Variable Display", 8)
FONT_LG  = ("Segoe UI Variable Display", 11)
FONT_XL  = ("Segoe UI Variable Display", 14, "bold")
FONT_MONO= ("Consolas", 9)


# ── Sprite renderer: draws the pet on a Canvas ───────────────────────────────

class PetSprite:
    """
    现代可爱风格宠物精灵 (Modern chibi-style pet sprite).
    All drawn with tkinter Canvas primitives — no image files.
    States: idle | happy | sleepy | talking | listening | thinking
    """
    def __init__(self, canvas: tk.Canvas, cx: int, cy: int, scale: float = 1.0):
        self.canvas = canvas
        self.cx = cx
        self.cy = cy
        self.scale = scale
        self.t = 0.0
        self.state = "idle"
        self.blink_t = 0.0
        self.next_blink = random.uniform(2, 5)
        self._items = []

    def _s(self, v): return v * self.scale
    def _x(self, dx=0): return self.cx + self._s(dx)
    def _y(self, dy=0): return self.cy + self._s(dy) + self._breathe_offset()

    def _breathe_offset(self):
        if self.state == "sleepy":
            return self._s(math.sin(self.t * 0.8) * 2)
        return self._s(math.sin(self.t * 1.5) * 1.2)

    def _sway_offset(self):
        if self.state == "happy":
            return self._s(math.sin(self.t * 4) * 4)
        return self._s(math.sin(self.t * 0.7) * 0.8)

    def _draw_oval(self, x, y, rx, ry, **kw):
        item = self.canvas.create_oval(x-rx, y-ry, x+rx, y+ry, **kw)
        self._items.append(item)
        return item

    def _draw_rect(self, x1, y1, x2, y2, r=0, **kw):
        if r > 0:
            item = self._rounded_rect(x1, y1, x2, y2, r, **kw)
        else:
            item = self.canvas.create_rectangle(x1, y1, x2, y2, **kw)
        self._items.append(item)
        return item

    def _rounded_rect(self, x1, y1, x2, y2, r, **kw):
        pts = [
            x1+r, y1,  x2-r, y1,
            x2, y1,    x2, y1+r,
            x2, y2-r,  x2, y2,
            x2-r, y2,  x1+r, y2,
            x1, y2,    x1, y2-r,
            x1, y1+r,  x1, y1,
            x1+r, y1,
        ]
        item = self.canvas.create_polygon(pts, smooth=True, **kw)
        self._items.append(item)
        return item

    def draw(self):
        for item in self._items:
            self.canvas.delete(item)
        self._items = []

        sway = self._sway_offset()
        cx = self.cx + sway
        cy = self._y()
        s = self._s

        # ── Shadow (soft) ──
        self._draw_oval(cx, cy + s(42), s(26), s(7),
                        fill="#060608", outline="", stipple="gray25")

        # ── Holo-Fox Body (Glassmorphism Core) ──
        # Instead of solid colors, we use dark transparent/stippled cores with bright neon borders
        body_bounce = 1.0 + math.sin(self.t * 1.5) * 0.02
        
        # Outer neon aura (body)
        self._draw_oval(cx, cy + s(30), s(18), s(15) * body_bounce,
                        fill="", outline=C["holo_outline"], width=1.5)
        # Inner dark core
        self._draw_oval(cx, cy + s(30), s(16), s(13) * body_bounce,
                        fill=C["holo_core"], outline="", stipple="gray50")

        # ── Holo-Ears (Floating/Detached) ──
        # Left ear
        pts_left = [
            cx - s(20), cy - s(15), 
            cx - s(30), cy - s(35), 
            cx - s(12), cy - s(25)
        ]
        item = self.canvas.create_polygon(pts_left, fill=C["holo_core"], outline=C["holo_outline"], width=1.5, smooth=True)
        self._items.append(item)
        # Right ear
        pts_right = [
            cx + s(20), cy - s(15), 
            cx + s(30), cy - s(35), 
            cx + s(12), cy - s(25)
        ]
        item = self.canvas.create_polygon(pts_right, fill=C["holo_core"], outline=C["holo_outline"], width=1.5, smooth=True)
        self._items.append(item)

        # ── Head (Holographic Orb) ──
        self._draw_oval(cx, cy, s(28), s(26),
                        fill=C["holo_core"], outline=C["holo_outline"], width=1.5)
        
        # Internal glowing circuit/wireframe line
        arc_item = self.canvas.create_arc(
            cx - s(24), cy - s(24), cx + s(24), cy + s(24),
            start=45, extent=90, style="arc", outline=C["accent"], width=2
        )
        self._items.append(arc_item)

        # ── Eyes (Digital/Neon) ──
        self._draw_eyes(cx, cy)

        # ── Tail (Data Stream) ──
        tail_wave = math.sin(self.t * 3) * s(5)
        pts_tail = [
            cx + s(15), cy + s(35),
            cx + s(30), cy + s(40) + tail_wave,
            cx + s(40), cy + s(30) + tail_wave * 1.5
        ]
        item = self.canvas.create_line(pts_tail, fill=C["accent"], width=2.5, smooth=True)
        self._items.append(item)
        # Tail tip glow
        self._draw_oval(cx + s(40), cy + s(30) + tail_wave * 1.5, s(3), s(3), fill=C["glow"], outline="")

        # ── State overlays ──
        if self.state == "happy":
            self._draw_sparkles(cx, cy)
        if self.state in ("sleepy",):
            self._draw_zzz(cx, cy)
        if self.state == "talking":
            self._draw_talk_indicator(cx, cy)
        if self.state == "listening":
            self._draw_waveform(cx, cy)
        if self.state == "thinking":
            self._draw_thinking(cx, cy)

    def _draw_eyes(self, cx, cy):
        s = self._s
        is_blinking = self.blink_t < 0.15

        if self.state == "happy":
            # Happy crescents (^‿^) - Draw with raw lines instead of filled ovals
            for ex in [cx - s(10), cx + s(10)]:
                item = self.canvas.create_line(
                    ex - s(5), cy + s(2),
                    ex,        cy - s(3),
                    ex + s(5), cy + s(2),
                    fill=C["holo_eye"], width=2.5, smooth=True
                )
                self._items.append(item)
        elif is_blinking or self.state == "sleepy":
            # Closed — thin glowing horizontal line
            self.canvas.create_line(cx - s(15), cy, cx - s(5), cy, fill=C["holo_eye"], width=2)
            self.canvas.create_line(cx + s(5),  cy, cx + s(15), cy, fill=C["holo_eye"], width=2)
        else:
            # Open eyes — glowing vertical digital bars (like EVE or a robot)
            for ex in [cx - s(12), cx + s(12)]:
                self._draw_rect(ex - s(3), cy - s(6), ex + s(3), cy + s(6), r=s(3),
                                fill=C["holo_eye"], outline=C["glow"], width=1)

    def _draw_sparkles(self, cx, cy):
        s = self._s
        phase = self.t * 3
        positions = [(-35, -20), (38, -15), (-30, 10), (42, 20)]
        for i, (dx, dy) in enumerate(positions):
            alpha = (math.sin(phase + i * 1.5) + 1) / 2
            size = s(3 + alpha * 3)
            x = cx + s(dx)
            y = cy + s(dy) + math.sin(phase + i) * s(3)
            if alpha > 0.3:
                self._draw_oval(x, y, size, size, fill=C["glow"], outline="")
                # Star/cross points
                for angle in [0, 90]:
                    rad = math.radians(angle)
                    item = self.canvas.create_line(
                        x + math.cos(rad) * size * 2, y + math.sin(rad) * size * 2,
                        x - math.cos(rad) * size * 2, y - math.sin(rad) * size * 2,
                        fill=C["glow"], width=1
                    )
                    self._items.append(item)

    def _draw_zzz(self, cx, cy):
        s = self._s
        phase = self.t * 0.5
        for i, char in enumerate(["z", "Z", "Z"]):
            alpha_offset = (i * 0.5 + phase) % 1.5
            if alpha_offset < 1.0:
                x = cx + s(25 + i * 8)
                y = cy - s(20 + i * 10) - alpha_offset * s(10)
                font_size = 8 + i * 2
                item = self.canvas.create_text(
                    x, y, text=char,
                    font=("Segoe UI Variable Display", font_size, "bold"),
                    fill=C["accent2"]
                )
                self._items.append(item)

    def _draw_talk_indicator(self, cx, cy):
        s = self._s
        phase = int(self.t * 3) % 3
        for i in range(3):
            color = C["accent"] if i == phase else C["muted"]
            self._draw_rect(cx + s(-12 + i * 12) - s(3), cy - s(48) - s(3), 
                            cx + s(-12 + i * 12) + s(3), cy - s(48) + s(3), r=s(1),
                            fill=color, outline="")

    def _draw_waveform(self, cx, cy):
        """Animated waveform bars during voice recording (listening state)."""
        s = self._s
        bars = 5
        bar_w = s(3)
        gap = s(3)
        total_w = bars * bar_w + (bars - 1) * gap
        x0 = cx - total_w / 2
        for i in range(bars):
            h = s(5 + 10 * abs(math.sin(self.t * 5 + i * 0.8)))
            x = x0 + i * (bar_w + gap)
            y_top = cy - s(52) - h
            y_bot = cy - s(52) + h
            item = self.canvas.create_rectangle(
                x, y_top, x + bar_w, y_bot,
                fill=C["accent"], outline="", width=0,
            )
            self._items.append(item)

    def _draw_thinking(self, cx, cy):
        """Spinning holographic data rings during LLM processing."""
        s = self._s
        n = 3
        r = s(16)
        for i in range(n):
            angle = self.t * 3 + i * (2 * math.pi / n)
            x = cx + r * math.cos(angle)
            y = (cy - s(45)) + r * 0.3 * math.sin(angle)
            size = s(2 + math.sin(self.t * 4 + i) * 1.5)
            # Draw orbiting nodes
            self._draw_oval(x, y, size, size, fill=C["accent2"], outline=C["glow"], width=1)
        
        # Draw central glowing core for thinking
        core_pulse = 1.0 + math.sin(self.t * 8) * 0.2
        self._draw_oval(cx, cy - s(45), s(4)*core_pulse, s(4)*core_pulse, fill=C["accent"], outline="")

    def tick(self, dt: float):
        self.t += dt
        self.blink_t += dt
        if self.blink_t > self.next_blink:
            self.blink_t = 0.0
            self.next_blink = random.uniform(3, 7)

    def set_state(self, state: str):
        """idle | happy | sleepy | talking"""
        self.state = state


# ── Pet floating window ───────────────────────────────────────────────────────

class DesktopPet:
    PET_SIZE = 100   # canvas size

    def __init__(
        self,
        on_record_start: Callable,
        on_record_stop: Callable,
        on_chat: Callable,
        get_entries: Callable,
        get_reminders: Callable,
    ):
        self._on_record_start = on_record_start
        self._on_record_stop  = on_record_stop
        self._on_chat         = on_chat
        self._get_entries     = get_entries
        self._get_reminders   = get_reminders
        self._save_callback   = None

        self._recording  = False
        self._drag_x     = 0
        self._drag_y     = 0
        self._dragged    = False
        self._last_frame = time.time()
        self._idle_time  = 0.0
        self._IDLE_SLEEP = 600.0

        self._build_pet_window()
        self._build_panel()
        self._animate()

    # ── Pet window ────────────────────────────────────────────────────────────

    def _build_pet_window(self):
        self.root = tk.Tk()
        self.root.title("灵犀笔记")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95)
        self.root.config(bg="black")
        try:
            self.root.attributes("-transparentcolor", "black")
        except tk.TclError:
            pass

        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        size = self.PET_SIZE + 20
        self.root.geometry(f"{size}x{size + 30}+{sw - size - 20}+{sh - size - 80}")

        # Canvas for sprite
        self.canvas = tk.Canvas(
            self.root,
            width=size, height=size,
            bg="black", highlightthickness=0,
        )
        self.canvas.pack()

        # Name tag below pet
        self.name_tag = tk.Label(
            self.root, text="« L U M I »",
            font=("Consolas", 8, "bold"),
            bg="black", fg=C["holo_outline"],
        )
        self.name_tag.pack()

        # Sprite
        cx, cy = size // 2, size // 2 - 5
        self.sprite = PetSprite(self.canvas, cx, cy, scale=1.4)

        # Speech bubble
        self._bubble_items = []
        self._bubble_timer = 0

        # Drag & click
        self.canvas.bind("<ButtonPress-1>",   self._on_press)
        self.canvas.bind("<B1-Motion>",        self._on_drag)
        self.canvas.bind("<ButtonRelease-1>",  self._on_release)
        self.canvas.bind("<Button-3>",         self._show_menu)

        # Context menu
        self._menu = tk.Menu(self.root, tearoff=0,
                             bg=C["card"], fg=C["text"],
                             activebackground=C["accent"],
                             font=FONT)
        self._menu.add_command(label="📖 灵犀笔记",    command=self._toggle_panel)
        self._menu.add_command(label="🎙️ 开始录音",   command=self._toggle_record)
        self._menu.add_separator()
        self._menu.add_command(label="😴 切换休眠",   command=lambda: self.sprite.set_state("sleepy"))
        self._menu.add_command(label="😊 切换开心",   command=lambda: self.sprite.set_state("happy"))
        self._menu.add_command(label="🙂 普通状态",   command=lambda: self._reset_idle())
        self._menu.add_separator()
        self._menu.add_command(label="❌ 退出",        command=self._quit)

    def _reset_idle(self):
        """Call on any user interaction to reset idle timer and restore idle state."""
        self._idle_time = 0.0
        if self.sprite.state == "sleepy":
            self.sprite.set_state("idle")

    def _animate(self):
        now = time.time()
        dt = now - self._last_frame
        self._last_frame = now

        self.sprite.tick(dt)
        self.sprite.draw()

        # Bubble timer
        if self._bubble_timer > 0:
            self._bubble_timer -= dt
            if self._bubble_timer <= 0:
                self._clear_bubble()

        # Idle auto-sleep: if no interaction for _IDLE_SLEEP seconds → sleepy
        if self.sprite.state == "idle":
            self._idle_time += dt
            if self._idle_time >= self._IDLE_SLEEP:
                self.sprite.set_state("sleepy")
        elif self.sprite.state != "sleepy":
            # Any non-idle active state resets the idle counter
            self._idle_time = 0.0

        self.root.after(33, self._animate)  # ~30 fps

    # ── Speech bubble ─────────────────────────────────────────────────────────

    def show_bubble(self, text: str, duration: float = 4.0):
        """Show a floating speech bubble above the pet."""
        self._clear_bubble()
        self.sprite.set_state("talking")

        size = self.PET_SIZE + 20
        # Truncate
        if len(text) > 40:
            text = text[:38] + "…"

        # Bubble background
        bx, by = size // 2, 8
        bw = min(len(text) * 7 + 20, size - 4)
        bh = 30

        item1 = self.canvas.create_rectangle(
            bx - bw//2, by, bx + bw//2, by + bh,
            fill=C["card"], outline=C["accent"], width=1
        )
        item2 = self.canvas.create_text(
            bx, by + bh//2, text=text,
            font=FONT_SM, fill=C["text"], width=bw - 8
        )
        self._bubble_items = [item1, item2]
        self._bubble_timer = duration

    def _clear_bubble(self):
        for item in self._bubble_items:
            self.canvas.delete(item)
        self._bubble_items = []
        if self.sprite.state == "talking":
            self.sprite.set_state("idle")

    # ── Drag logic ────────────────────────────────────────────────────────────

    def _on_press(self, event):
        self._reset_idle()
        self._drag_x = event.x
        self._drag_y = event.y
        self._dragged = False

    def _on_drag(self, event):
        self._dragged = True
        dx = event.x - self._drag_x
        dy = event.y - self._drag_y
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")

    def _on_release(self, event):
        if not self._dragged:
            self._toggle_panel()
        self._dragged = False

    def _show_menu(self, event):
        self._menu.post(event.x_root, event.y_root)

    # ── Recording ─────────────────────────────────────────────────────────────

    def _toggle_record(self):
        self._reset_idle()
        if not self._recording:
            self._recording = True
            self.sprite.set_state("talking")
            self.show_bubble("🎙️ 录音中...", duration=60)
            self._on_record_start()
        else:
            self._recording = False
            self.show_bubble("⏳ 转写中...", duration=10)
            def do_transcribe():
                text = self._on_record_stop()
                self.root.after(0, lambda: self._on_transcript_done(text))
            threading.Thread(target=do_transcribe, daemon=True).start()

    def _on_transcript_done(self, text: str):
        if text:
            self._entry_text.delete("1.0", "end")
            self._entry_text.insert("1.0", text)
            self.show_bubble("✅ 转写完成！", duration=3)
            self._toggle_panel()
        else:
            self.show_bubble("没有录到声音 😅", duration=3)

    # ── Reminder popup ────────────────────────────────────────────────────────

    def show_reminder_popup(self, message: str):
        self.sprite.set_state("happy")
        self.show_bubble(f"⏰ {message[:20]}", duration=5)

        popup = tk.Toplevel(self.root)
        popup.title("⏰ 提醒")
        popup.geometry("360x180")
        popup.config(bg=C["bg"])
        popup.attributes("-topmost", True)

        tk.Label(popup, text="⏰  提醒时间到啦！",
                 font=FONT_LG, bg=C["bg"], fg=C["accent"]).pack(pady=(20, 8))
        tk.Label(popup, text=message, font=FONT,
                 bg=C["bg"], fg=C["text"], wraplength=300, justify="center").pack(padx=20)
        tk.Button(popup, text="  好的，知道了 ✓  ",
                  font=FONT, bg=C["success"], fg=C["bg"],
                  relief="flat", padx=8, pady=6,
                  command=popup.destroy).pack(pady=20)

    # ── Main panel ────────────────────────────────────────────────────────────

    def _build_panel(self):
        self.panel = tk.Toplevel(self.root)
        self.panel.title("灵犀笔记 — AI 日记本")
        self.panel.geometry("520x680")
        self.panel.minsize(480, 600)
        self.panel.config(bg=C["bg"])
        self.panel.protocol("WM_DELETE_WINDOW", self._hide_panel)
        self.panel.withdraw()

        # ── Header (Sleek minimalist tech header) ──
        hdr = tk.Frame(self.panel, bg=C["panel"], pady=0)
        hdr.pack(fill="x")
        # Top ultra-thin accent neon line
        tk.Frame(hdr, bg=C["accent"], height=1).pack(fill="x")
        hdr_inner = tk.Frame(hdr, bg=C["panel"], pady=14)
        hdr_inner.pack(fill="x")

        left_col = tk.Frame(hdr_inner, bg=C["panel"])
        left_col.pack(side="left", padx=(20, 0))
        tk.Label(left_col, text="✦ LUMILOG",
                 font=FONT_XL, bg=C["panel"], fg=C["text"]).pack(anchor="w")
        tk.Label(left_col, text="AI MEMORY CORE",
                 font=("Segoe UI Variable Display", 7, "bold"), bg=C["panel"], fg=C["accent"]).pack(anchor="w")

        # Record button in header (flat icon)
        self._hdr_rec_btn = tk.Button(
            hdr_inner, text="🎙️",
            font=("Segoe UI", 12),
            bg=C["panel"], fg=C["text"],
            activebackground=C["card"], activeforeground=C["accent"],
            relief="flat", cursor="hand2", bd=0,
            command=self._toggle_record_panel,
        )
        self._hdr_rec_btn.pack(side="right", padx=20)

        # Bottom thin separator
        tk.Frame(hdr, bg=C["card2"], height=1).pack(fill="x")

        # ── Tabs (Modern flat underline style) ──
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("X.TNotebook",     background=C["bg"], borderwidth=0, tabmargins=0)
        style.configure("X.TNotebook.Tab", background=C["bg"], foreground=C["muted"],
                         padding=[20, 10], font=FONT_LG, borderwidth=0, focuscolor=C["bg"])
        style.map("X.TNotebook.Tab",
                  background=[("selected", C["card"])],
                  foreground=[("selected", C["accent"])])

        nb = ttk.Notebook(self.panel, style="X.TNotebook")
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        # Build tabs
        t1 = tk.Frame(nb, bg=C["bg"]); nb.add(t1, text="  📝 写日记  "); self._build_write_tab(t1)
        t2 = tk.Frame(nb, bg=C["bg"]); nb.add(t2, text="  📚 历史  ");   self._build_history_tab(t2)
        t3 = tk.Frame(nb, bg=C["bg"]); nb.add(t3, text="  ⏰ 提醒  ");   self._build_reminders_tab(t3)
        t4 = tk.Frame(nb, bg=C["bg"]); nb.add(t4, text="  💬 聊天  ");   self._build_chat_tab(t4)

    # ── Write tab ─────────────────────────────────────────────────────────────

    def _build_write_tab(self, parent):
        padx = 14  # shared horizontal padding

        # Recording controls
        rec_frame = tk.Frame(parent, bg=C["bg"])
        rec_frame.pack(fill="x", padx=padx, pady=(14, 4))

        self._rec_btn = tk.Button(
            rec_frame, text="🎙️  开始录音",
            font=FONT, bg=C["accent"], fg="white",
            activebackground=C["glow"],
            relief="flat", padx=14, pady=7,
            cursor="hand2",
            command=self._toggle_record_panel,
        )
        self._rec_btn.pack(side="left")

        self._rec_status = tk.Label(rec_frame, text="点击录音，或直接在下方输入",
                                    font=FONT_SM, bg=C["bg"], fg=C["muted"])
        self._rec_status.pack(side="left", padx=10)

        # Separator
        sep = tk.Frame(parent, bg=C["card2"], height=1)
        sep.pack(fill="x", padx=padx, pady=6)

        # Text entry
        tk.Label(parent, text="日记内容", font=FONT_SM,
                 bg=C["bg"], fg=C["muted"]).pack(anchor="w", padx=padx, pady=4)

        self._entry_text = scrolledtext.ScrolledText(
            parent, height=9,
            font=("Segoe UI", 10),
            bg=C["card"], fg=C["text"],
            insertbackground=C["glow"],
            relief="flat", padx=10, pady=10,
            wrap="word", selectbackground=C["accent2"],
        )
        self._entry_text.pack(fill="both", padx=14, pady=2)

        # Save button
        save_frame = tk.Frame(parent, bg=C["bg"])
        save_frame.pack(fill="x", padx=14, pady=8)

        tk.Button(
            save_frame, text=" ✦  保存 & 分析  ",
            font=FONT, bg=C["card2"], fg=C["text"],
            activebackground=C["accent"], activeforeground=C["bg"],
            relief="flat", padx=16, pady=8, bd=1,
            cursor="hand2",
            command=self._save_entry,
        ).pack(side="left")

        self._save_status = tk.Label(save_frame, text="", font=FONT_SM,
                                     bg=C["bg"], fg=C["success"])
        self._save_status.pack(side="left", padx=10)

        # Reflection
        sep2 = tk.Frame(parent, bg=C["card2"], height=1)
        sep2.pack(fill="x", padx=14, pady=6)

        tk.Label(parent, text="✦ REASONING", font=("Consolas", 8, "bold"),
                 bg=C["bg"], fg=C["accent2"]).pack(anchor="w", padx=14)

        self._reflection_box = scrolledtext.ScrolledText(
            parent, height=4,
            font=("Segoe UI Variable Display", 10),
            bg=C["card2"], fg=C["text"],
            relief="flat", padx=10, pady=10,
            wrap="word", state="disabled",
        )
        self._reflection_box.pack(fill="x", padx=14, pady=(2, 4))

        # ── Memory query answer box (shown only when query detected) ──
        self._query_frame = tk.Frame(parent, bg=C["bg"])
        # (packed/unpacked dynamically)

        tk.Label(self._query_frame, text="🧠 MEMORY RETRIEVED",
                 font=("Consolas", 8, "bold"), bg=C["bg"], fg=C["accent"]).pack(anchor="w", padx=14)
        self._query_box = scrolledtext.ScrolledText(
            self._query_frame, height=5,
            font=("Segoe UI Variable Display", 10),
            bg="#060b14", fg=C["accent"],
            relief="flat", padx=10, pady=10,
            wrap="word", state="disabled", highlightthickness=1, highlightbackground=C["holo_outline"]
        )
        self._query_box.pack(fill="both", padx=14, pady=(2, 14))

    def _toggle_record_panel(self):
        self._reset_idle()
        if not self._recording:
            self._recording = True
            self._rec_btn.config(text="⏹  停止录音", bg=C["error"])
            self._rec_status.config(text="🔴 录音中...", fg=C["error"])
            self.sprite.set_state("talking")
            self._on_record_start()
        else:
            self._recording = False
            self._rec_btn.config(text="🎙️  开始录音", bg=C["accent"])
            self._rec_status.config(text="⏳ 正在转写...", fg=C["warn"])
            self.panel.update()
            self.sprite.set_state("idle")

            def do():
                text = self._on_record_stop()
                self.root.after(0, lambda: self._on_panel_transcript(text))
            threading.Thread(target=do, daemon=True).start()

    def _on_panel_transcript(self, text: str):
        self._rec_status.config(text="✅ 转写完成", fg=C["success"])
        if text:
            cur = self._entry_text.get("1.0", "end-1c").strip()
            self._entry_text.insert("end", ("\n" if cur else "") + text)

    def _save_entry(self):
        self._reset_idle()
        text = self._entry_text.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("提示", "日记内容为空哦 ✦")
            return
        self._save_status.config(text="思考中...", fg=C["warn"])
        self._set_reflection("💭 灵犀正在理解你的输入...")
        self._set_query_answer(None)  # clear previous answer
        self.sprite.set_state("thinking")

        def ai_work():
            result = self._save_callback(text)
            self.root.after(0, lambda: self._after_save(result))
        threading.Thread(target=ai_work, daemon=True).start()

    def _after_save(self, result: dict):
        input_type   = result.get("input_type", "diary")
        reflection   = result.get("reflection")
        query_answer = result.get("query_answer")
        reminders    = result.get("reminders", [])

        # Show reflection if present
        if reflection:
            self._set_reflection(reflection)
        else:
            self._set_reflection("")

        # Show query answer if present
        self._set_query_answer(query_answer)

        self._entry_text.delete("1.0", "end")

        count  = len(reminders)
        badges = []
        if input_type in ("query", "both"):
            badges.append("🧠 记忆查询")
        if count:
            badges.append(f"⏰ {count} 个提醒")
        status = "✅ 已保存" + (f"  ·  {'  ·  '.join(badges)}" if badges else "")
        self._save_status.config(text=status, fg=C["success"])

        self.sprite.set_state("happy")
        preview = (query_answer or reflection or "")[:30]
        if preview:
            self.show_bubble(preview + "...", duration=5)

        self._refresh_history()
        self._refresh_reminders()

    def _set_reflection(self, text: str):
        self._reflection_box.config(state="normal")
        self._reflection_box.delete("1.0", "end")
        if text:
            self._reflection_box.insert("1.0", text)
        self._reflection_box.config(state="disabled")

    def _set_query_answer(self, text: str | None):
        """Show or hide the memory query answer box."""
        if text:
            self._query_frame.pack(fill="x", pady=(0, 4))
            self._query_box.config(state="normal")
            self._query_box.delete("1.0", "end")
            self._query_box.insert("1.0", text)
            self._query_box.config(state="disabled")
        else:
            self._query_frame.pack_forget()

    # ── History tab ───────────────────────────────────────────────────────────

    def _build_history_tab(self, parent):
        btn_f = tk.Frame(parent, bg=C["bg"])
        btn_f.pack(fill="x", padx=14, pady=(14, 4))

        tk.Label(btn_f, text="MEMORIES", font=("Consolas", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(side="left")
        tk.Button(btn_f, text="↻ SYNC", font=("Consolas", 8),
                  bg=C["card2"], fg=C["muted"],
                  relief="flat", padx=12, bd=0, activebackground=C["card"], activeforeground=C["text"],
                  command=self._refresh_history).pack(side="right")

        # Scrollable area
        self._hist_canvas = tk.Canvas(parent, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(parent, orient="vertical", command=self._hist_canvas.yview)
        self._hist_canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._hist_canvas.pack(fill="both", expand=True, padx=(14, 0))

        self._hist_inner = tk.Frame(self._hist_canvas, bg=C["bg"])
        self._hist_canvas.create_window((0, 0), window=self._hist_inner, anchor="nw")
        self._hist_inner.bind("<Configure>", lambda e: self._hist_canvas.configure(
            scrollregion=self._hist_canvas.bbox("all")))

    def _refresh_history(self):
        for w in self._hist_inner.winfo_children():
            w.destroy()

        entries = self._get_entries()
        if not entries:
            tk.Label(self._hist_inner, text="\n[ EMPTY DATA STREAM ]\nWrite your first entry ✦",
                     font=("Consolas", 9), bg=C["bg"], fg=C["muted"]).pack(pady=30)
            return

        for e in entries:
            self._make_entry_card(self._hist_inner, e)

    def _make_entry_card(self, parent, e: dict):
        # Cyber-card style (borderless, dark, solid padding)
        card_outer = tk.Frame(parent, bg=C["holo_core"], pady=1, padx=1) # Thin border effect
        card_outer.pack(fill="x", pady=(0, 10))
        
        card = tk.Frame(card_outer, bg=C["card"], pady=14, padx=16, cursor="hand2")
        card.pack(fill="both", expand=True)

        # Header row
        hrow = tk.Frame(card, bg=C["card"])
        hrow.pack(fill="x")

        tk.Label(hrow, text=f"LOG  {e['date']}",
                 font=("Consolas", 8), bg=C["card"], fg=C["holo_outline"]).pack(side="left")

        try:
            tags = __import__("json").loads(e["tags"])
            if tags:
                tag_str = " ".join([f"[{t}]" for t in tags[:3]])
                tk.Label(hrow, text=tag_str, font=("Consolas", 8),
                         bg=C["card"], fg=C["accent2"]).pack(side="right")
        except Exception:
            pass

        # Content preview
        preview = e["text"][:160] + ("..." if len(e["text"]) > 160 else "")
        tk.Label(card, text=preview, font=FONT,
                 bg=C["card"], fg=C["text"],
                 wraplength=440, justify="left").pack(anchor="w", pady=(10, 0))

        # Reflection
        if e.get("reflection"):
            sep = tk.Frame(card, bg=C["card2"], height=1)
            sep.pack(fill="x", pady=(10, 6))
            tk.Label(card, text=f"✦ {e['reflection'][:120]}",
                     font=("Segoe UI Variable Display", 8), bg=C["card"], fg=C["glow"],
                     wraplength=440, justify="left").pack(anchor="w")

    # ── Reminders tab ─────────────────────────────────────────────────────────

    def _build_reminders_tab(self, parent):
        btn_f = tk.Frame(parent, bg=C["bg"])
        btn_f.pack(fill="x", padx=14, pady=(14, 4))

        tk.Label(btn_f, text="PENDING ALERTS", font=("Consolas", 10, "bold"), bg=C["bg"], fg=C["text"]).pack(side="left")
        tk.Button(btn_f, text="↻ SYNC", font=("Consolas", 8),
                  bg=C["card2"], fg=C["muted"],
                  relief="flat", padx=12, bd=0, activebackground=C["card"], activeforeground=C["text"],
                  command=self._refresh_reminders).pack(side="right")

        self._rem_canvas = tk.Canvas(parent, bg=C["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(parent, orient="vertical", command=self._rem_canvas.yview)
        self._rem_canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._rem_canvas.pack(fill="both", expand=True, padx=(14, 0))

        self._rem_inner = tk.Frame(self._rem_canvas, bg=C["bg"])
        self._rem_canvas.create_window((0, 0), window=self._rem_inner, anchor="nw")
        self._rem_inner.bind("<Configure>", lambda e: self._rem_canvas.configure(
            scrollregion=self._rem_canvas.bbox("all")))

    def _refresh_reminders(self):
        for w in self._rem_inner.winfo_children():
            w.destroy()

        reminders = self._get_reminders()
        if not reminders:
            tk.Label(self._rem_inner, text="\n[ NO ACTIVE ALERTS ]✦",
                     font=("Consolas", 9), bg=C["bg"], fg=C["muted"]).pack(pady=30)
            return

        for r in reminders:
            card_outer = tk.Frame(self._rem_inner, bg=C["warn"], pady=1, padx=0)
            card_outer.pack(fill="x", pady=(0, 10))
            card = tk.Frame(card_outer, bg=C["card"], pady=12, padx=16)
            card.pack(fill="both", expand=True)

            tk.Label(card, text=f"T-{r['time']}",
                     font=("Consolas", 8, "bold"), bg=C["card"], fg=C["warn"]).pack(anchor="w")
            tk.Label(card, text=r["message"], font=FONT,
                     bg=C["card"], fg=C["text"],
                     wraplength=440, justify="left").pack(anchor="w", pady=(8, 0))

    # ── Chat tab ──────────────────────────────────────────────────────────────

    def _build_chat_tab(self, parent):
        self._chat_log = scrolledtext.ScrolledText(
            parent, height=20,
            font=("Segoe UI Variable Display", 10),
            bg=C["panel"], fg=C["text"],
            insertbackground=C["glow"],
            relief="flat", padx=16, pady=16,
            wrap="word", state="disabled",
            selectbackground=C["accent2"],
        )
        self._chat_log.pack(fill="both", expand=True, padx=14, pady=(14, 4))

        # Tag styles
        self._chat_log.tag_config("pet",   foreground=C["accent"])
        self._chat_log.tag_config("user",  foreground=C["accent2"])
        self._chat_log.tag_config("time",  foreground=C["muted"], font=("Consolas", 8))
        self._chat_log.tag_config("body",  foreground=C["text"])
        self._chat_log.tag_config("hint",  foreground=C["muted"])

        # Input area
        inp = tk.Frame(parent, bg=C["panel"])
        inp.pack(fill="x", padx=14, pady=(0, 14))

        self._chat_input = tk.Entry(
            inp, font=("Segoe UI Variable Display", 10),
            bg=C["card"], fg=C["text"],
            insertbackground=C["glow"],
            relief="flat",
        )
        self._chat_input.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 10))
        self._chat_input.bind("<Return>", lambda e: self._send_chat())

        tk.Button(
            inp, text="ENTER",
            font=("Consolas", 10, "bold"), bg=C["accent"], fg=C["panel"],
            relief="flat", padx=16, pady=8, bd=0, activebackground=C["glow"],
            command=self._send_chat, cursor="hand2"
        ).pack(side="right")

        # Memory hint
        tk.Label(parent, text="💡 TERMINAL: Query past entries or chat directly.",
                 font=("Consolas", 8), bg=C["bg"], fg=C["muted"],
                 wraplength=480).pack(padx=14, pady=(0, 8))

        self._append_chat("LUMI", "System online. Ready to sync.")

    def _send_chat(self):
        self._reset_idle()
        msg = self._chat_input.get().strip()
        if not msg:
            return
        self._chat_input.delete(0, "end")
        self._append_chat("USER", msg)
        self.sprite.set_state("talking")

        def do():
            reply = self._on_chat(msg)
            self.root.after(0, lambda: self._on_chat_reply(reply))
        threading.Thread(target=do, daemon=True).start()

    def _on_chat_reply(self, reply: str):
        self._append_chat("LUMI", reply)
        self.sprite.set_state("happy")
        self.show_bubble(reply[:25] + "...", duration=4)

    def _append_chat(self, sender: str, text: str):
        self._chat_log.config(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        tag = "pet" if sender != "USER" else "user"
        self._chat_log.insert("end", f"\n[{ts}] ", "time")
        self._chat_log.insert("end", f"{sender}\n", tag)
        self._chat_log.insert("end", f"{text}\n", "body")
        self._chat_log.see("end")
        self._chat_log.config(state="disabled")

    # ── Panel helpers ─────────────────────────────────────────────────────────

    def _toggle_panel(self):
        self._reset_idle()
        if self.panel.winfo_viewable():
            self._hide_panel()
        else:
            self.panel.deiconify()
            self.panel.lift()
            self._refresh_history()
            self._refresh_reminders()

    def _hide_panel(self):
        self.panel.withdraw()

    def _quit(self):
        self.root.quit()
        self.root.destroy()

    def set_save_callback(self, callback: Callable):
        self._save_callback = callback

    def run(self):
        self.root.mainloop()
