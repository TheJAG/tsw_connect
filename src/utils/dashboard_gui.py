import tkinter as tk
from datetime import datetime
from typing import Dict, List, Callable

from src.config.constants import BG_COLOR, ACCENT_COLOR, CARD_COLOR, TEXT_COLOR, STOP_COLOR


class DashboardGUI:
    def __init__(
        self, 
        data: Dict[str, List], 
        stop_callback: Callable[[], None],
        start_time: datetime
    ):
        self.data = data
        self.stop_callback = stop_callback
        self.start_time = start_time
        self.running = True
        
        # GUI Setup
        self.root = tk.Tk()
        self.root.title("TSW Connect Dashboard")
        self.root.geometry("400x320")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_COLOR)

        self._setup_ui()
        self._update_gui()

    def _setup_ui(self):
        # Main Container
        main_frame = tk.Frame(self.root, bg=BG_COLOR, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        lbl_title = tk.Label(
            main_frame, 
            text="DATA COLLECTOR", 
            font=('Helvetica', 14, 'bold'), 
            bg=BG_COLOR,
            fg=ACCENT_COLOR,
            pady=10
        )
        lbl_title.pack(anchor="center")

        # Time Display
        self.lbl_timer = tk.Label(
            main_frame,
            text="00:00:00",
            font=('Courier New', 24, 'bold'),
            bg=BG_COLOR,
            fg="#ffffff"
        )
        self.lbl_timer.pack(pady=(0, 20))

        # Stats Container (Grid layout for side-by-side cards)
        stats_container = tk.Frame(main_frame, bg=BG_COLOR)
        stats_container.pack(fill=tk.X, pady=(0, 20))
        stats_container.grid_columnconfigure(0, weight=1)
        stats_container.grid_columnconfigure(1, weight=1)

        # Player Stat Card
        frame_player = tk.Frame(stats_container, bg=CARD_COLOR, padx=10, pady=10)
        frame_player.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        tk.Label(
            frame_player, 
            text="PLAYER", 
            font=('Helvetica', 8), 
            bg=CARD_COLOR,
            fg=TEXT_COLOR
        ).pack()
        
        self.lbl_player_val = tk.Label(
            frame_player, 
            text="0", 
            font=('Helvetica', 18, 'bold'), 
            bg=CARD_COLOR,
            fg="#ffffff"
        )
        self.lbl_player_val.pack()

        # AI Stat Card
        frame_ai = tk.Frame(stats_container, bg=CARD_COLOR, padx=10, pady=10)
        frame_ai.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        tk.Label(
            frame_ai, 
            text="AI VEHICLES", 
            font=('Helvetica', 8), 
            bg=CARD_COLOR,
            fg=TEXT_COLOR
        ).pack()
        
        self.lbl_ai_val = tk.Label(
            frame_ai, 
            text="0", 
            font=('Helvetica', 18, 'bold'), 
            bg=CARD_COLOR,
            fg="#ffffff"
        )
        self.lbl_ai_val.pack()

        # Styled Stop Button
        self.btn_stop = tk.Button(
            main_frame,
            text="STOP & SAVE",
            font=('Helvetica', 11, 'bold'),
            bg=STOP_COLOR,
            fg="#ffffff",
            activebackground="#d65d72",
            activeforeground="#ffffff",
            relief="flat",
            pady=8,
            cursor="hand2",
            command=self._on_stop
        )
        self.btn_stop.pack(fill=tk.X, pady=10)

        # Handle window close button (X)
        self.root.protocol("WM_DELETE_WINDOW", self._on_stop)

    def _on_stop(self):
        self.btn_stop.config(text="SAVING...", state="disabled", bg="#444444")
        self.root.update()
        self.running = False
        self.stop_callback()  # Notify the main app
        self.root.quit()

    def _update_gui(self):
        if self.running:
            # Update Stats
            self.lbl_player_val.config(text=f"{len(self.data['player']):,}")
            self.lbl_ai_val.config(text=f"{len(self.data['ai']):,}")
            
            # Update Timer
            elapsed = datetime.now() - self.start_time
            elapsed_str = datetime.utcfromtimestamp(elapsed.total_seconds()).strftime('%H:%M:%S')
            self.lbl_timer.config(text=elapsed_str)
            
            self.root.after(100, self._update_gui)

    def run(self):
        self.root.mainloop()
        try:
            self.root.destroy()
        except tk.TclError:
            pass