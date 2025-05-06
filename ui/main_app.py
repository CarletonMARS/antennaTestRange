import customtkinter as ctk
from PIL import Image
import settings
from ui.manual_control import ManualControlWindow

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.ManualControlWindow = None
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        #self.attributes("-fullscreen", True)

        self.geometry("3440x1440")
        self.title("ANTENNA TEST RANGE CONTROLLER ---- DEPARTMENT OF ELECTRONICS")
        self.attributes('-fullscreen', True)
        #BANNER IMAGE
        image_path = "Carleton_Logo.png"
        image = Image.open(image_path)
        self.ctk_image = ctk.CTkImage(light_image=image, size=(300, 200))
        self.label = ctk.CTkLabel(self, image=self.ctk_image, text="")
        self.label.grid(row=0, column=2, padx=10, pady=10)

        # #VNA SOFT FRONT PANEL
        # self.control_vna_button = ctk.CTkButton(self, text="VNA SOFT PANEL", command=self.SFP)
        # self.control_vna_button.grid(row=1, column=0, padx=10, pady=10)

        #POSITIONER MANUAL CONTROL
        self.control_positioner = ctk.CTkButton(self, text="MANUAL POSITIONER CONTROL", command=self.positioner_manual_control)
        self.control_positioner.grid(row=1, column=2, padx=10, pady=10)
        #
        # #3d spherical pattern generation
        # self.spherical_pattern = ctk.CTkButton(self, text="3D SPHERICAL PATTERN", command=self.three_d_spherical_pattern)
        # self.spherical_pattern.grid(row=2, column=0, padx=10, pady=10)

        #TEXT BOX
        self.textbox = ctk.CTkTextbox(self, height=600, width=1500, wrap="word")
        self.textbox.grid(row=3, column=0, padx=10, pady=10)

        #close button
        self.close_button = ctk.CTkButton(self, text="CLOSE", command=self.close)
        self.close_button.grid(row=4, column=2, padx=10, pady=10)

    # def SFP(self):
    #     sfp = SFP(self)

    def positioner_manual_control(self):
         self.ManualControlWindow = ManualControlWindow(self)

    def update_textbox(self, text):
        """Updates the textbox with new text."""
        self.textbox.delete("1.0", "end")  # Clear previous text
        self.textbox.insert("end", text)  # Insert new text

    # def three_d_spherical_pattern(self):
    #     threeD = threeDpat(self)

    def close(self):
        self.destroy()