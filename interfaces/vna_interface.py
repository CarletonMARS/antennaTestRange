import pyvisa
class VNAController:
    def connect(self):
        try:
            self.rm = pyvisa.ResourceManager()
            self.VNA = self.rm.open_resource("GPIB0::16::INSTR")
            print(self.VNA.query("*IDN?"))
            self.connectButton.configure(text='Connected', state=tk.DISABLED)
            self.connected_flag = True
        except pyvisa.VisaIOError:
            print("FAILED TO CONNECT TO VNA")