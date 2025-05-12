import sys

import customtkinter as ctk
from PIL import Image
import settings
from ui.manual_control import ManualControlWindow
from ui.pattern_wizard import PatternWizard
from ui.vna_panel import VNAFrontPanel
from interfaces.vna_interface import VNAController
from interfaces.serial_interface import SerialController


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("ANTENNA TEST RANGE CONTROLLER ---- DEPARTMENT OF ELECTRONICS")
        self.attributes('-fullscreen', True)

        # BANNER IMAGE
        image_path = "images/Carleton_Logo.png"
        image = Image.open(image_path)
        self.ctk_image = ctk.CTkImage(light_image=image, size=(300, 200))
        self.banner = ctk.CTkLabel(self, image=self.ctk_image, text="")
        self.banner.grid(row=0, column=2, padx=10, pady=10)

        # Controllers to be initialized
        self.vna_ctrl = None
        self.serial_ctrl = None

        # Connect Buttons
        self.btn_connect_serial = ctk.CTkButton(self, text="Connect Positioner", command=self.connect_serial)
        self.btn_connect_serial.grid(row=1, column=0, padx=20, pady=10)

        self.btn_connect_vna = ctk.CTkButton(self, text="Connect VNA", command=self.vna_connect)
        self.btn_connect_vna.grid(row=1, column=1, padx=20, pady=10)

        # POSITIONER MANUAL CONTROL
        self.btn_manual_control = ctk.CTkButton(
            self,
            text="MANUAL POSITIONER CONTROL",
            command=self.open_manual_control,
            state="disabled"
        )
        self.btn_manual_control.grid(row=2, column=0, padx=20, pady=10)

        # VNA SOFT FRONT PANEL
        self.btn_vna_control = ctk.CTkButton(
            self,
            text="VNA SOFT PANEL",
            command=self.open_vna_panel,
            state="disabled"
        )
        self.btn_vna_control.grid(row=2, column=1, padx=20, pady=10)

        # 3d spherical pattern generation
        self.btn_pattern_wizard = ctk.CTkButton(
            self,
            text="3D SPHERICAL PATTERN",
            command=self.open_pattern_wizard,
            state="disabled"
        )
        self.btn_pattern_wizard.grid(row=3, column=0, columnspan=2, padx=20, pady=10)
        # status label
        self.status = ctk.CTkLabel(self, text="Not Connected")
        self.status.grid(row=4, column=0, columnspan=2, pady=20)

        # close button
        self.btn_close = ctk.CTkButton(self, text="CLOSE", command=self.close)
        self.btn_close.grid(row=5, column=0, columnspan=2, pady=20)

    def open_vna_panel(self):
        VNAFrontPanel(self, self.vna_ctrl)

    def open_manual_control(self):
        ManualControlWindow(self, self.serial_ctrl)

    def open_pattern_wizard(self):
        PatternWizard(self, self.vna_ctrl, self.serial_ctrl)

    def vna_connect(self):
        try:
            self.vna_ctrl = VNAController(settings.GPIB_ADDRESS)
            idn = self.vna_ctrl.connect()
            self.status.configure(text=f"VNA Connected: {idn}")
            self.btn_vna_control.configure(state="normal")
            self.btn_connect_vna.configure(text="VNA Connected", state="disabled")
            if self.serial_ctrl:
                self.btn_pattern_wizard.configure(state="normal")
        except Exception as e:
            self.status.configure(text=f"VNA failed: {e}")

    def connect_serial(self):
        try:
            self.serial_ctrl = SerialController(settings.COM_PORT, settings.BAUD_RATE)
            self.serial_ctrl.query_position()
            self.btn_connect_serial.configure(text="Positioner Connected", state="disabled")
            self.status.configure(text="Positioner Connected")
            self.btn_manual_control.configure(state="normal")
            if self.vna_ctrl:
                self.btn_pattern_wizard.configure(state="normal")
        except Exception as e:
            self.status.configure(text=f"Connection Failed: {e}")

    def update_textbox(self, text):
        """Updates the textbox with new text."""
        self.textbox.delete("1.0", "end")  # Clear previous text
        self.textbox.insert("end", text)  # Insert new text

    def close(self):
        """Closes interface connections and program"""
        if self.vna_ctrl:
            self.vna_ctrl.close()
        if self.serial_ctrl:
            self.serial_ctrl.close()
        self.destroy()
        sys.exit(0)
