"""
AutoClick - clique automático em qualquer ponto da tela.

Uso:
  F9  -> captura a posição atual do mouse como ponto de clique
  F10 -> inicia/para o clique automático (funciona mesmo com outra janela em foco)

Obs.: F6/F7 foram evitados de propósito porque Chrome e Edge usam essas
teclas para "focar a barra de endereço" e "navegação por cursor de texto"
(o popup "Ativar Caret Browsing?"), o que atrapalharia o uso.

Compilar em .exe standalone:
  python -m PyInstaller --onefile --windowed --name AutoClick autoclick.py
"""

import ctypes
import random
import threading
import time
import tkinter as tk
from tkinter import ttk

from pynput import keyboard, mouse

# Timer do Windows tem resolução padrão de ~15ms; isso deixa sleeps curtos
# (cliques rápidos) mais precisos e consistentes.
try:
    ctypes.windll.winmm.timeBeginPeriod(1)
except Exception:
    pass

mouse_controller = mouse.Controller()

lock = threading.Lock()
state = {
    "point": None,       # (x, y) em coordenadas de tela
    "running": False,
    "infinite": True,
    "max_clicks": 100,
    "interval_ms": 100,
    "count": 0,
}

stop_event = threading.Event()
click_thread = None


def click_loop():
    while not stop_event.is_set():
        with lock:
            point = state["point"]
            interval = max(1, state["interval_ms"]) / 1000.0
            infinite = state["infinite"]
            max_clicks = state["max_clicks"]
        if point is None:
            with lock:
                state["running"] = False
            return

        # Pequena variação de posição/tempo a cada clique: alguns sites (ex.
        # testadores de mouse) filtram cliques repetidos no pixel exato e no
        # intervalo exato como "chatter" de switch com defeito.
        jitter_point = (point[0] + random.randint(-2, 2), point[1] + random.randint(-2, 2))
        mouse_controller.position = jitter_point
        mouse_controller.click(mouse.Button.left, 1)

        with lock:
            state["count"] += 1
            done = (not infinite) and state["count"] >= max_clicks
        if done:
            with lock:
                state["running"] = False
            return

        time.sleep(interval * random.uniform(0.85, 1.15))


def start_clicking():
    global click_thread
    with lock:
        if state["point"] is None or state["running"]:
            return
        state["running"] = True
        state["count"] = 0
    stop_event.clear()
    click_thread = threading.Thread(target=click_loop, daemon=True)
    click_thread.start()


def stop_clicking():
    with lock:
        state["running"] = False
    stop_event.set()


def toggle_clicking():
    with lock:
        running = state["running"]
    if running:
        stop_clicking()
    else:
        start_clicking()


def capture_point():
    x, y = mouse_controller.position
    with lock:
        state["point"] = (int(x), int(y))


# ---------------- Atalhos globais (funcionam mesmo sem a janela em foco) ----------------
hotkeys = keyboard.GlobalHotKeys({"<f9>": capture_point, "<f10>": toggle_clicking})
hotkeys.start()


# ---------------- Interface ----------------
root = tk.Tk()
root.title("AutoClick")
root.resizable(False, False)
root.configure(bg="#14141f")

PAD = {"padx": 14, "pady": 6}

style = ttk.Style(root)
try:
    style.theme_use("clam")
except tk.TclError:
    pass
style.configure("TFrame", background="#14141f")
style.configure("TLabel", background="#14141f", foreground="#e8e8f0", font=("Segoe UI", 10))
style.configure("Hint.TLabel", foreground="#9a9ab0", font=("Segoe UI", 9))
style.configure("Status.TLabel", foreground="#c9c9dc", font=("Segoe UI", 10, "bold"))
style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
style.configure("TCheckbutton", background="#14141f", foreground="#e8e8f0")

frame = ttk.Frame(root, style="TFrame")
frame.pack(fill="both", expand=True, **PAD)

ttk.Label(frame, text="🖱️  AutoClick", font=("Segoe UI", 14, "bold")).grid(
    row=0, column=0, columnspan=3, sticky="w", pady=(0, 8)
)

ttk.Label(
    frame,
    text="1) Passe o mouse sobre o ponto desejado e pressione F9\n2) Pressione F10 para iniciar/parar (funciona em qualquer janela)",
    style="Hint.TLabel",
    justify="left",
).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 10))

point_label = ttk.Label(frame, text="Ponto: nenhum selecionado", style="Status.TLabel")
point_label.grid(row=2, column=0, columnspan=3, sticky="w", pady=(0, 10))

ttk.Label(frame, text="Intervalo entre cliques (ms):").grid(row=3, column=0, columnspan=3, sticky="w")
interval_var = tk.StringVar(value="100")
interval_entry = ttk.Entry(frame, textvariable=interval_var, width=10)
interval_entry.grid(row=4, column=0, sticky="w", pady=(2, 8))


def apply_interval(*_args):
    try:
        ms = max(1, int(float(interval_var.get())))
    except ValueError:
        ms = 100
    with lock:
        state["interval_ms"] = ms


interval_var.trace_add("write", apply_interval)

preset_frame = ttk.Frame(frame, style="TFrame")
preset_frame.grid(row=4, column=1, columnspan=2, sticky="w", pady=(2, 8))
for label, ms in (("Lento", 500), ("Médio", 100), ("Rápido", 20), ("Insano", 5)):
    ttk.Button(preset_frame, text=label, width=7, command=lambda v=ms: interval_var.set(str(v))).pack(
        side="left", padx=2
    )

infinite_var = tk.BooleanVar(value=True)


def apply_infinite():
    with lock:
        state["infinite"] = infinite_var.get()
    max_clicks_entry.configure(state="disabled" if infinite_var.get() else "normal")


ttk.Checkbutton(frame, text="Clique infinito", variable=infinite_var, command=apply_infinite).grid(
    row=5, column=0, columnspan=3, sticky="w", pady=(0, 4)
)

ttk.Label(frame, text="Quantidade de cliques:").grid(row=6, column=0, sticky="w")
max_clicks_var = tk.StringVar(value="100")
max_clicks_entry = ttk.Entry(frame, textvariable=max_clicks_var, width=10, state="disabled")
max_clicks_entry.grid(row=6, column=1, sticky="w")


def apply_max_clicks(*_args):
    try:
        n = max(1, int(float(max_clicks_var.get())))
    except ValueError:
        n = 100
    with lock:
        state["max_clicks"] = n


max_clicks_var.trace_add("write", apply_max_clicks)

toggle_btn = ttk.Button(frame, text="Iniciar (F10)", command=toggle_clicking)
toggle_btn.grid(row=7, column=0, columnspan=3, sticky="we", pady=(12, 4))

status_label = ttk.Label(frame, text="Parado · 0 cliques", style="Hint.TLabel")
status_label.grid(row=8, column=0, columnspan=3, sticky="w")


def refresh_ui():
    with lock:
        point = state["point"]
        running = state["running"]
        count = state["count"]
        infinite = state["infinite"]
        max_clicks = state["max_clicks"]

    point_label.configure(text=f"Ponto: {point}" if point else "Ponto: nenhum selecionado")
    toggle_btn.configure(text="Parar (F10)" if running else "Iniciar (F10)")
    total = f"{count} cliques" if infinite else f"{count} / {max_clicks} cliques"
    status_label.configure(text=f"{'Rodando' if running else 'Parado'} · {total}")

    root.after(120, refresh_ui)


def on_close():
    stop_clicking()
    hotkeys.stop()
    try:
        ctypes.windll.winmm.timeEndPeriod(1)
    except Exception:
        pass
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_close)
refresh_ui()
root.mainloop()
