from PIL import Image
import customtkinter as ctk
from interfaces.serial_interface import SerialController
import settings


class ManualControlWindow(ctk.CTkToplevel):
    def __init__(self, parent, serial_ctrl: SerialController):
        self.connected = False
        super().__init__(parent)
        self.ctrl = serial_ctrl
        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.lift()
        self.after(10, lambda: self.focus_force())
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.geometry("3440x1440")
        self.title("POSITIONER MANUAL CONTROL")

        # BANNER IMAGE
        image_path = "DUO5.png"
        image = Image.open(image_path)
        self.ctk_image = ctk.CTkImage(light_image=image, size=(200, 200))
        self.label = ctk.CTkLabel(self, image=self.ctk_image, text="")
        self.label.grid(row=0, column=4, padx=10, pady=10)
        # X -10
        self.xminus10_button = ctk.CTkButton(self, text="X -10", command=self.xminus10)
        self.xminus10_button.grid(row=2, column=0, pady=10, padx=10)

        # X -1
        self.xminus1_button = ctk.CTkButton(self, text="X -1", command=self.xminus1)
        self.xminus1_button.grid(row=2, column=1, pady=10, padx=10)

        # X -0.1
        self.xminus0p1_button = ctk.CTkButton(self, text="X -0.1", command=self.xminus0p1)
        self.xminus0p1_button.grid(row=2, column=2, pady=10, padx=10)

        # X -0.02
        self.xminus0p02_button = ctk.CTkButton(self, text="X -0.02", command=self.xminus0p02)
        self.xminus0p02_button.grid(row=2, column=3, pady=10, padx=10)

        # X 10
        self.xplus10_button = ctk.CTkButton(self, text="X +10", command=self.xplus10)
        self.xplus10_button.grid(row=2, column=8, pady=10, padx=10)

        # X 1
        self.xplus1_button = ctk.CTkButton(self, text="X +1", command=self.xplus1)
        self.xplus1_button.grid(row=2, column=7, pady=10, padx=10)

        # X 0.1
        self.xplus0p1_button = ctk.CTkButton(self, text="X +0.1", command=self.xplus0p1)
        self.xplus0p1_button.grid(row=2, column=6, pady=10, padx=10)

        # X 0.02
        self.xplus0p02_button = ctk.CTkButton(self, text="X +0.02", command=self.xplus0p02)
        self.xplus0p02_button.grid(row=2, column=5, pady=10, padx=10)

        ##################################################################################################

        # Y -10
        self.yminus10_button = ctk.CTkButton(self, text="Y -10", command=self.yminus10)
        self.yminus10_button.grid(row=3, column=0, pady=10, padx=10)

        # Y -1
        self.yminus1_button = ctk.CTkButton(self, text="Y -1", command=self.yminus1)
        self.yminus1_button.grid(row=3, column=1, pady=10, padx=10)

        # Y -0.1
        self.yminus0p1_button = ctk.CTkButton(self, text="Y -0.1", command=self.yminus0p1)
        self.yminus0p1_button.grid(row=3, column=2, pady=10, padx=10)

        # Y -0.02
        self.yminus0p02_button = ctk.CTkButton(self, text="Y -0.02", command=self.yminus0p02)
        self.yminus0p02_button.grid(row=3, column=3, pady=10, padx=10)

        # Y 10
        self.yplus10_button = ctk.CTkButton(self, text="Y +10", command=self.yplus10)
        self.yplus10_button.grid(row=3, column=8, pady=10, padx=10)

        # Y 1
        self.yplus1_button = ctk.CTkButton(self, text="Y +1", command=self.yplus1)
        self.yplus1_button.grid(row=3, column=7, pady=10, padx=10)

        # Y 0.1
        self.yplus0p1_button = ctk.CTkButton(self, text="Y +0.1", command=self.yplus0p1)
        self.yplus0p1_button.grid(row=3, column=6, pady=10, padx=10)

        # Y 0.02
        self.yplus0p02_button = ctk.CTkButton(self, text="Y +0.02", command=self.yplus0p02)
        self.yplus0p02_button.grid(row=3, column=5, pady=10, padx=10)

        # Home X
        self.HomeX_button = ctk.CTkButton(self, text="HomeX", command=self.homex)
        self.HomeX_button.grid(row=4, column=1, pady=10, padx=10)

        # Home Y
        self.HomeY_button = ctk.CTkButton(self, text="HomeY", command=self.homey)
        self.HomeY_button.grid(row=4, column=2, pady=10, padx=10)

        # Home A
        self.HomeA_button = ctk.CTkButton(self, text="HomeA", command=self.homea)
        self.HomeA_button.grid(row=4, column=3, pady=10, padx=10)

        # Home All
        self.HomeALL_button = ctk.CTkButton(self, text="Home All", command=self.home)
        self.HomeALL_button.grid(row=4, column=4, pady=10, padx=10)

        # Goto 000
        self.goto0_button = ctk.CTkButton(self, text="GOTO 0,0,0", command=self.goto0)
        self.goto0_button.grid(row=4, column=7, pady=10, padx=10)

        # Close
        self.close_button = ctk.CTkButton(self, text='CLOSE', command=self.close)
        self.close_button.grid(row=6, column=4, padx=1, pady=1)

        # TEXTBOX
        self.textbox = ctk.CTkTextbox(self, height=100, width=1500, wrap="word")
        self.textbox.grid(row=5, column=4, padx=10, pady=10)

    def connect_to_controller(self):
        try:
            x, y, z, a, b, c = self.ctrl.query_position()
            self.update_textbox(f"Connected. Position at connection time is X{x} Y{y} A{a}\n")
            self.connected = True
        except Exception as e:
            self.update_textbox(f"Failed to connect: {e}")

    def update_textbox(self, text):
        """Updates the textbox with new text."""
        self.textbox.delete("1.0", "end")  # Clear previous text
        self.textbox.insert("end", text)  # Insert new text

    def xminus10(self):
        self.move_and_refresh(-10, 0)

    def xminus1(self):
        self.move_and_refresh(-1, 0)

    def xminus0p1(self):
        self.move_and_refresh(-0.1, 0)

    def xminus0p02(self):
        self.move_and_refresh(-0.02, 0)

    def xplus0p02(self):
        self.move_and_refresh(0.02, 0)

    def xplus0p1(self):
        self.move_and_refresh(0.1, 0)

    def xplus1(self):
        self.move_and_refresh(1, 0)

    def xplus10(self):
        self.move_and_refresh(10, 0)

    def yminus10(self):
        self.move_and_refresh(0, -10)

    def yminus1(self):
        self.move_and_refresh(0, -1)

    def yminus0p1(self):
        self.move_and_refresh(0, -0.1)

    def yminus0p02(self):
        self.move_and_refresh(0, -0.02)

    def yplus0p02(self):
        self.move_and_refresh(0, 0.02)

    def yplus0p1(self):
        self.move_and_refresh(0, 0.1)

    def yplus1(self):
        self.move_and_refresh(0, 1)

    def yplus10(self):
        self.move_and_refresh(0, 10)

    def homex(self):
        self.ctrl.home_x()
        self.refresh(45)

    def homey(self):
        self.ctrl.home_y()
        self.refresh(45)

    def homea(self):
        self.ctrl.home_a()
        self.refresh(45)

    def home(self):
        self.ctrl.home_xya()
        self.refresh(45)

    def goto0(self):
        self.zero_and_refresh()

    def get_position(self):

        try:
            x, y, z, a, *_ = self.ctrl.query_position()
            self.update_textbox(f"Current Position: X{x} Y{y} A{a}")
            return x, y, z, a
        except Exception as e:
            self.update_textbox(f"Error in getting position: {str(e)}")
            return None, None, None, None

    def refresh(self, timeout=10):
        try:
            self.ctrl.wait_for_idle(timeout)
        except RuntimeError as e:
            return self.update_textbox(f"Move timeout: {e}")
        x1, y1, *_ = self.ctrl.query_position()
        self.update_textbox(f"Current Position: X{x1} Y{y1} A0")

    def move_and_refresh(self, dx, dy):
        x0, y0, *_ = self.ctrl.query_position()
        target_x = x0 + dx
        target_y = y0 + dy
        self.ctrl.move_to(target_x, target_y)
        self.refresh()

    def zero_and_refresh(self):

        self.ctrl.move_to(0, 0)
        self.refresh()

    def close(self):

        self.destroy()
