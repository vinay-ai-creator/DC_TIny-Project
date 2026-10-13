"""
Distributed Token Ring Simulator
A beginner-friendly GUI simulation of token-based mutual exclusion.

Requirements: Python 3.10+ (Tkinter is included with most standard Python installs)
Run: python main.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import math
from collections import deque


class TokenRingSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Distributed Token Ring Simulator")
        self.root.geometry("1080x760")
        self.root.minsize(900, 650)

        self.node_count = 5
        self.token_holder = 0
        self.requests = [False] * self.node_count
        self.waiting_queue = deque()
        self.in_critical_section = None
        self.running = False
        self.after_id = None
        self.step_count = 0
        self.completed_requests = 0
        self.token_history = []
        self.node_names = [f"P{i + 1}" for i in range(self.node_count)]

        self._build_ui()
        self._draw_ring()
        self._refresh_status()
        self._log("Simulation ready. P1 initially holds the token.")
        self._log("Click 'Request Resource' to make a process request the shared resource.")

    def _build_ui(self):
        header = ttk.Frame(self.root, padding=(14, 12))
        header.pack(fill="x")
        ttk.Label(
            header,
            text="Distributed Token Ring Simulator",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w")
        ttk.Label(
            header,
            text="Visualize token passing and mutual exclusion among distributed processes",
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(3, 0))

        main = ttk.Frame(self.root, padding=(12, 0, 12, 12))
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main)
        left.pack(side="left", fill="both", expand=True)

        right = ttk.Frame(main, width=330)
        right.pack(side="right", fill="y", padx=(12, 0))
        right.pack_propagate(False)

        ring_frame = ttk.LabelFrame(left, text="Token Ring Network", padding=8)
        ring_frame.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(ring_frame, bg="#f7f9fc", highlightthickness=0, height=470)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _event: self._draw_ring())

        stats = ttk.LabelFrame(left, text="Simulation Statistics", padding=10)
        stats.pack(fill="x", pady=(10, 0))
        self.stats_var = tk.StringVar()
        ttk.Label(stats, textvariable=self.stats_var, font=("Segoe UI", 10)).pack(anchor="w")

        controls = ttk.LabelFrame(right, text="Controls", padding=10)
        controls.pack(fill="x")
        self.start_button = ttk.Button(controls, text="Start Auto Simulation", command=self.start)
        self.start_button.pack(fill="x", pady=3)
        self.pause_button = ttk.Button(controls, text="Pause", command=self.pause, state="disabled")
        self.pause_button.pack(fill="x", pady=3)
        self.step_button = ttk.Button(controls, text="Pass Token (One Step)", command=self.step)
        self.step_button.pack(fill="x", pady=3)
        self.request_button = ttk.Button(controls, text="Request Resource", command=self.request_random)
        self.request_button.pack(fill="x", pady=3)
        self.random_button = ttk.Button(controls, text="Generate Random Requests", command=self.generate_requests)
        self.random_button.pack(fill="x", pady=3)
        self.reset_button = ttk.Button(controls, text="Reset Simulation", command=self.reset)
        self.reset_button.pack(fill="x", pady=3)

        request_frame = ttk.LabelFrame(right, text="Request From Specific Process", padding=10)
        request_frame.pack(fill="x", pady=(10, 0))
        ttk.Label(request_frame, text="Select process:").pack(anchor="w")
        self.process_choice = tk.StringVar(value="P2")
        self.process_box = ttk.Combobox(
            request_frame,
            textvariable=self.process_choice,
            values=self.node_names,
            state="readonly"
        )
        self.process_box.pack(fill="x", pady=(4, 6))
        ttk.Button(request_frame, text="Submit Request", command=self.request_selected).pack(fill="x")

        status_frame = ttk.LabelFrame(right, text="Current State", padding=10)
        status_frame.pack(fill="x", pady=(10, 0))
        self.token_var = tk.StringVar()
        self.cs_var = tk.StringVar()
        self.queue_var = tk.StringVar()
        ttk.Label(status_frame, textvariable=self.token_var, wraplength=290).pack(anchor="w", pady=2)
        ttk.Label(status_frame, textvariable=self.cs_var, wraplength=290).pack(anchor="w", pady=2)
        ttk.Label(status_frame, textvariable=self.queue_var, wraplength=290).pack(anchor="w", pady=2)

        log_frame = ttk.LabelFrame(right, text="Event Log", padding=8)
        log_frame.pack(fill="both", expand=True, pady=(10, 0))
        self.log_text = tk.Text(log_frame, height=13, wrap="word", state="disabled", font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        footer = ttk.Label(
            self.root,
            text="Model: one logical token circulates in a ring; only the token holder may enter the critical section.",
            padding=(12, 4),
            font=("Segoe UI", 9, "italic")
        )
        footer.pack(fill="x")

    def _node_positions(self):
        width = max(self.canvas.winfo_width(), 500)
        height = max(self.canvas.winfo_height(), 400)
        cx, cy = width / 2, height / 2
        radius = min(width * 0.34, height * 0.34)
        positions = []
        for i in range(self.node_count):
            angle = -math.pi / 2 + (2 * math.pi * i / self.node_count)
            positions.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
        return positions

    def _draw_ring(self):
        if not hasattr(self, "canvas"):
            return
        self.canvas.delete("all")
        positions = self._node_positions()

        # Draw directional links first, behind nodes.
        for i, (x1, y1) in enumerate(positions):
            x2, y2 = positions[(i + 1) % self.node_count]
            dx, dy = x2 - x1, y2 - y1
            length = math.hypot(dx, dy) or 1
            pad = 38
            sx, sy = x1 + dx * pad / length, y1 + dy * pad / length
            ex, ey = x2 - dx * pad / length, y2 - dy * pad / length
            self.canvas.create_line(sx, sy, ex, ey, fill="#9aa8ba", width=3, arrow=tk.LAST, arrowshape=(10, 12, 5))

        # Draw a subtle center label.
        cx, cy = self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2
        self.canvas.create_text(cx, cy - 12, text="TOKEN RING", font=("Segoe UI", 15, "bold"), fill="#526174")
        self.canvas.create_text(cx, cy + 12, text="Shared Resource", font=("Segoe UI", 10), fill="#526174")

        for i, (x, y) in enumerate(positions):
            is_token = i == self.token_holder
            is_cs = self.in_critical_section == i
            has_request = self.requests[i]
            fill = "#f4b942" if is_token else "#ffffff"
            outline = "#b87800" if is_token else "#3f638a"
            width = 4 if is_token else 2
            if is_cs:
                fill, outline, width = "#8ee0b3", "#16834b", 4
            elif has_request and not is_token:
                fill, outline = "#ffd9d9", "#c34242"

            r = 31
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill, outline=outline, width=width)
            self.canvas.create_text(x, y-5, text=self.node_names[i], font=("Segoe UI", 12, "bold"), fill="#1c2733")
            label = "TOKEN" if is_token else ("IN CS" if is_cs else ("REQUEST" if has_request else ""))
            if label:
                self.canvas.create_text(x, y+12, text=label, font=("Segoe UI", 7, "bold"), fill="#1c2733")

        # Legend
        legend_y = self.canvas.winfo_height() - 22
        items = [
            ("#f4b942", "Token holder"),
            ("#ffd9d9", "Waiting request"),
            ("#8ee0b3", "Critical section")
        ]
        start_x = 18
        for color, label in items:
            self.canvas.create_oval(start_x, legend_y-6, start_x+12, legend_y+6, fill=color, outline="#7c8794")
            self.canvas.create_text(start_x+18, legend_y, text=label, anchor="w", font=("Segoe UI", 8), fill="#394655")
            start_x += 120

    def _log(self, message):
        if not hasattr(self, "log_text"):
            return
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _refresh_status(self):
        self.token_var.set(f"Token holder: {self.node_names[self.token_holder]}")
        if self.in_critical_section is None:
            self.cs_var.set("Critical section: nobody")
        else:
            self.cs_var.set(f"Critical section: {self.node_names[self.in_critical_section]}")
        queue_names = [self.node_names[i] for i in self.waiting_queue]
        self.queue_var.set("Waiting queue: " + (", ".join(queue_names) if queue_names else "empty"))
        self.stats_var.set(
            f"Token passes: {self.step_count}     Completed resource accesses: {self.completed_requests}     "
            f"Pending requests: {sum(self.requests)}"
        )
        self._draw_ring()

    def request_selected(self):
        name = self.process_choice.get()
        self._request(self.node_names.index(name))

    def request_random(self):
        candidates = [i for i in range(self.node_count) if not self.requests[i] and self.in_critical_section != i]
        if not candidates:
            self._log("No new request added: every process already has a pending request or is using the resource.")
            return
        self._request(random.choice(candidates))

    def _request(self, index):
        if self.requests[index] or self.in_critical_section == index:
            self._log(f"{self.node_names[index]} already has a pending request or is using the resource.")
            return
        self.requests[index] = True
        self.waiting_queue.append(index)
        self._log(f"{self.node_names[index]} requests access to the shared resource.")
        self._refresh_status()

    def generate_requests(self):
        candidates = [i for i in range(self.node_count) if not self.requests[i] and self.in_critical_section != i]
        if not candidates:
            self._log("No eligible processes for additional requests.")
            return
        count = random.randint(1, len(candidates))
        chosen = random.sample(candidates, count)
        for i in chosen:
            self.requests[i] = True
            self.waiting_queue.append(i)
            self._log(f"{self.node_names[i]} requests access to the shared resource.")
        self._refresh_status()

    def step(self):
        self.step_count += 1
        current = self.token_holder

        if self.in_critical_section is not None:
            # The current simulated access finishes before the token moves on.
            finished = self.in_critical_section
            self.in_critical_section = None
            self.requests[finished] = False
            try:
                self.waiting_queue.remove(finished)
            except ValueError:
                pass
            self.completed_requests += 1
            self._log(f"{self.node_names[finished]} leaves the critical section and releases the resource.")
            self.token_holder = (finished + 1) % self.node_count
            self._log(f"Token passed from {self.node_names[finished]} to {self.node_names[self.token_holder]}.")
        elif self.requests[current]:
            # Token holder with a pending request gets exclusive access.
            self.in_critical_section = current
            self._log(f"{self.node_names[current]} enters the critical section (exclusive access granted).")
        else:
            next_holder = (current + 1) % self.node_count
            self.token_holder = next_holder
            self._log(f"No request at {self.node_names[current]}; token passed to {self.node_names[next_holder]}.")

        self._refresh_status()

    def start(self):
        if self.running:
            return
        self.running = True
        self.start_button.configure(state="disabled")
        self.pause_button.configure(state="normal")
        self._log("Automatic simulation started.")
        self._auto_step()

    def _auto_step(self):
        if not self.running:
            return
        self.step()
        self.after_id = self.root.after(1000, self._auto_step)

    def pause(self):
        self.running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.start_button.configure(state="normal")
        self.pause_button.configure(state="disabled")
        self._log("Simulation paused.")

    def reset(self):
        self.pause()
        self.token_holder = 0
        self.requests = [False] * self.node_count
        self.waiting_queue.clear()
        self.in_critical_section = None
        self.step_count = 0
        self.completed_requests = 0
        self.token_history.clear()
        self._log("Simulation reset. P1 holds the token.")
        self._refresh_status()

    def on_close(self):
        self.pause()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = TokenRingSimulator(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
