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

        self.theta_step = None
        self.phi_step = None
        self.freq_stop = None
        self.freq_points = None
        self.freq_start = None
        self.csv_path = None

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
        self.params_frame = ctk.CTkFrame(self)
        self.params_frame.pack(pady=5, fill="x", padx=10)

        self.entries = {}

        param_labels = [
            ("Theta Step (°)", "theta_step"),
            ("Phi Step (°)", "phi_step"),
            ("Freq Start (GHz)", "freq_start"),
            ("Freq Stop (GHz)", "freq_stop"),
            ("Freq Points", "freq_step"),
            ("CSV Path", "csv_path"),
        ]

        for idx, (label_text, var_name) in enumerate(param_labels):
            label = ctk.CTkLabel(self.params_frame, text=label_text)
            entry = ctk.CTkEntry(self.params_frame, width=100)
            label.grid(row=0, column=idx, padx=2, sticky="w")
            entry.grid(row=1, column=idx, padx=2)
            self.entries[var_name] = entry

        self.label = ctk.CTkLabel(self, text="Click 'Start Scan' to begin spherical scan")
        self.start_btn = ctk.CTkButton(self, text="Start Scan", command=self.start_scan_thread)
        self.abort_btn = ctk.CTkButton(self, text="Abort", command=self.abort_scan)
        self.close_btn = ctk.CTkButton(self, text="Close", command=self.handle_close)

        for w in (self.label, self.start_btn, self.abort_btn, self.close_btn):
            w.pack(pady=5)

        self.fig = plt.figure(figsize=(5, 4))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def start_scan_thread(self):
        try:
            self.theta_step = float(self.entries["theta_step"].get())
            self.phi_step = float(self.entries["phi_step"].get())
            self.freq_start = float(self.entries["freq_start"].get())
            self.freq_stop = float(self.entries["freq_stop"].get())
            self.freq_points = float(self.entries["freq_step"].get())
            self.csv_path = self.entries["csv_path"].get().strip()
        except ValueError:
            self.label.configure(text="Invalid input: please check all fields.")
            return
        try:
            self.freq_setup()
        except RuntimeError as e:
            self.label.configure(text=str(e))
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
        theta_range = np.arange(0, 360 + self.theta_step, self.theta_step)
        theta_range = theta_range[theta_range <= 360]

        phi_range = np.arange(0, 90 + self.phi_step, self.phi_step)
        phi_range = phi_range[phi_range <= 90]

        self.data.clear()

        for theta in theta_range:
            if self.abort_flag.is_set():
                break
            for phi in phi_range:
                if self.abort_flag.is_set():
                    break

                try:
                    self.serial.move_to(theta, phi)
                    self.serial.wait_for_idle()
                except Exception as e:
                    return self.safe_gui_update(self.label, text=f"Positioner error: {e}")

                try:
                    freqs, mags = self.vna.read_trace()
                    # Save full trace to CSV
                    for f, m in zip(freqs, mags):
                        self.data.append((theta, phi, f, m))

                    # Use first frequency's magnitude for 3D plotting
                    self.update_3d_plot(theta, phi, mags[0])
                    self.save_csv(self.csv_path)
                except Exception as e:
                    return self.safe_gui_update(self.label, text=f"VNA error: {e}")

        self.save_csv(self.csv_path)
        if not self.abort_flag.is_set():
            self.safe_gui_update(self.label, text="Scan complete. Results saved.")
        else:
            self.safe_gui_update(self.label, text="Scan aborted.")
        self.safe_gui_update(self.start_btn, state="normal")

    def save_csv(self, filename="scan_results.csv"):
        import csv
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Theta (deg)", "Phi (deg)", "Frequency (GHz)", "Magnitude (dB)"])
            for row in self.data:
                writer.writerow(row)

    def update_3d_plot(self, theta, phi, db_val):
        r = 10 ** (db_val / 20)
        theta_rad = np.radians(theta)
        phi_rad = np.radians(phi)

        x = r * np.cos(phi_rad) * np.cos(theta_rad)
        y = r * np.cos(phi_rad) * np.sin(theta_rad)
        z = r * np.sin(phi_rad)

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

    def freq_setup(self):
        """Configures the VNA with frequency parameters using exact step size."""

        num_points = int(self.freq_points)
        try:
            self.vna.write(f"STAR {self.freq_start}GHZ")
            self.vna.write(f"STOP {self.freq_stop}GHZ")
            self.vna.write(f"POIN {num_points}")
            self.vna.write("OUTPLIML")


        except Exception as e:
            raise RuntimeError(f"VNA config error: {e}")
