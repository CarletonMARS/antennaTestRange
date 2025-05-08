
import threading
import csv

import tkinter as tk
import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class PatternWizard(ctk.CTkToplevel):
    def __init__(self, parent, vna_ctrl, serial_ctrl):
        super().__init__(parent)
        self.title("3D Pattern Wizard")
        self.attributes("-topmost", True)
        self.geometry("800x600")

        # Silence any stray Tcl bgerror popups
        try:
            self.tk.call("rename", "bgerror", "orig_bgerror")
        except tk.TclError:
            pass
        self.tk.createcommand("bgerror", lambda *args: None)

        self.vna = vna_ctrl
        self.serial = serial_ctrl

        self.abort_flag = threading.Event()
        self.data = []
        self.alive = True

        # for tracking pending after() callbacks
        self._after_ids = []
        self._orig_after = super().after
        self.after = self._schedule  # monkey-patch instance .after

        # keep handle on our scan thread
        self.scan_thread = None

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.handle_close)

    def _schedule(self, delay_ms, callback=None, *args):
        """Wraps after(): only schedules if widget still exists, records IDs."""
        if not self.winfo_exists():
            return None
        if callback:
            aid = self._orig_after(delay_ms, callback, *args)
        else:
            aid = self._orig_after(delay_ms)
        self._after_ids.append(aid)
        return aid

    def create_widgets(self):
        self.label     = ctk.CTkLabel(self, text="Click 'Start Scan' to begin spherical scan")
        self.start_btn = ctk.CTkButton(self, text="Start Scan", command=self.start_scan_thread)
        self.abort_btn = ctk.CTkButton(self, text="Abort",      command=self.abort_scan)
        self.close_btn = ctk.CTkButton(self, text="Close",      command=self.handle_close)

        for w in (self.label, self.start_btn, self.abort_btn, self.close_btn):
            w.pack(pady=5)

        self.fig    = plt.figure(figsize=(5,4))
        self.ax     = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def start_scan_thread(self):
        self.abort_flag.clear()
        self.start_btn.configure(state="disabled")
        self.label.configure(text="Scanning...")
        self.data.clear()
        self.ax.cla()

        # launch the thread and keep a handle
        self.scan_thread = threading.Thread(target=self.run_scan, daemon=True)
        self.scan_thread.start()

    def abort_scan(self):
        self.abort_flag.set()
        self.label.configure(text="Abort requested...")

    def handle_close(self):
        # 1) signal scan to stop
        self.alive = False
        self.abort_flag.set()

        # 2) cancel all pending callbacks
        for aid in self._after_ids:
            try:
                super().after_cancel(aid)
            except Exception:
                pass
        self._after_ids.clear()

        # 3) wait briefly for the scan thread to exit
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=1)

        # 4) destroy only this Toplevel
        try:
            self.destroy()
        except Exception:
            pass


    def run_scan(self):
        theta_range = np.linspace(0, 360, 36)
        phi_range   = np.linspace(0, 90, 10)

        for phi in phi_range:
            if self.abort_flag.is_set(): break
            for theta in theta_range:
                if self.abort_flag.is_set(): break

                try:
                    self.serial.move_to(theta, phi)
                    self.serial.wait_for_idle()
                except Exception as e:
                    return self.safe_gui_update(self.label, text=f"Positioner error: {e}")

                try:
                    _, mags = self.vna.read_trace()
                    db_val = mags[0]
                    self.data.append((theta, phi, db_val))
                    self.update_3d_plot(theta, phi, db_val)
                except Exception as e:
                    return self.safe_gui_update(self.label, text=f"VNA error: {e}")

        # final status update
        if not self.abort_flag.is_set():
            self.save_csv()
            self.safe_gui_update(self.label, text="Scan complete. Results saved.")
        else:
            self.safe_gui_update(self.label, text="Scan aborted.")
        self.safe_gui_update(self.start_btn, state="normal")

    def save_csv(self):
        try:
            with open("spherical_scan_results.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Theta (deg)", "Phi (deg)", "Magnitude (dB)"])
                writer.writerows(self.data)
        except Exception as e:
            self.safe_gui_update(self.label, text=f"CSV save error: {e}")

    def update_3d_plot(self, theta, phi, db_val):
        r     = 10**(db_val/20)
        theta_rad = np.radians(theta)
        phi_rad = np.radians(phi)
        x = r * np.sin(phi_rad) * np.cos(theta_rad)
        y = r * np.sin(phi_rad) * np.sin(theta_rad)
        z = r * np.cos(phi_rad)

        def draw():
            if not self.winfo_exists(): return
            self.ax.scatter(x, y, z, s=10)
            self.ax.set_title("Live 3D Pattern")
            self.canvas.draw()

        if self.alive:
            self.after(0, draw)

    def safe_gui_update(self, widget, **kwargs):
        def upd():
            if not self.winfo_exists(): return
            try:
                widget.configure(**kwargs)
            except Exception:
                pass
        if self.alive:
            self.after(0, upd)

    #TODO: ADD FREQUENCY EDITOR AND DATA ACQUISITION PARAMETERS BOXES