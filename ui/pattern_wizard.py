class threeDpat(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__()

        self.theta = None
        self.phi = None
        self.stop = None
        self.step = None
        self.start = None
        self.path = None
        self.IFbandwidth = None
        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        self.lift()
        self.after(10, lambda: self.focus_force())
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.geometry("3440x1440")
        self.title("3D SPHERICAL PATTERN WIZARD")

        #SET START FREQUENCY
        self.fStart = ctk.CTkLabel(self, text="START FREQUENCY (GHz)", font=("Arial", 16), text_color="white")
        self.fStart.grid(row=0, column=0, padx=10, pady=10)

        self.efStart = ctk.CTkEntry(self, placeholder_text="DEFAULT = 1GHz")
        self.efStart.grid(row=0, column=1, padx=10, pady=10)

        self.start_result = ctk.CTkLabel(self, text="")
        self.start_result.grid(row=0, column=2, padx=10, pady=10)

        #SET STOP FREQUENCY
        self.fStop = ctk.CTkLabel(self, text="STOP FREQUENCY (GHz)", font=("Arial", 16), text_color="white")
        self.fStop.grid(row=1, column=0, padx=10, pady=10)

        self.efStop = ctk.CTkEntry(self, placeholder_text="DEFAULT = 20GHz")
        self.efStop.grid(row=1, column=1, padx=10, pady=10)

        self.stop_result = ctk.CTkLabel(self, text="")
        self.stop_result.grid(row=1, column=2, padx=10, pady=10)

        #SET IF BANDWIDTH
        self.IFB = ctk.CTkLabel(self, text='IF BANDWIDTH', font=("Arial", 16), text_color='white')
        self.IFB.grid(row=2, column=0, padx=10, pady=10)

        self.eIFB = ctk.CTkEntry(self, placeholder_text="enter IFB")
        self.eIFB.grid(row=2, column=1, padx=10, pady=10)

        self.IFB_result = ctk.CTkLabel(self, text="")
        self.IFB_result.grid(row=2, column=2, padx=10, pady=10)

        #SET STEP SIZE
        self.fStep = ctk.CTkLabel(self, text="STEP SIZE (GHz)", font=("Arial", 16), text_color="white")
        self.fStep.grid(row=3, column=0, padx=10, pady=10)

        self.efStep = ctk.CTkEntry(self, placeholder_text="DEFAULT = 1GHz")
        self.efStep.grid(row=3, column=1, padx=10, pady=10)

        self.step_result = ctk.CTkLabel(self, text="")
        self.step_result.grid(row=3, column=2, padx=10, pady=10)

        #SET THETA RESOLUTION
        self.thetaStep = ctk.CTkLabel(self, text="STEP SIZE - THETA (degrees)", font=("Arial", 16), text_color="white")
        self.thetaStep.grid(row=4, column=0, padx=10, pady=10)

        self.eTheta = ctk.CTkEntry(self, placeholder_text="DEFAULT = 1")
        self.eTheta.grid(row=4, column=1, padx=10, pady=10)

        self.theta_result = ctk.CTkLabel(self, text="")
        self.theta_result.grid(row=4, column=2, padx=10, pady=10)

        # SET PHI RESOLUTION
        self.phiStep = ctk.CTkLabel(self, text="STEP SIZE - PHI (degrees)", font=("Arial", 16), text_color="white")
        self.phiStep.grid(row=5, column=0, padx=10, pady=10)

        self.ePhi = ctk.CTkEntry(self, placeholder_text="DEFAULT = 1")
        self.ePhi.grid(row=5, column=1, padx=10, pady=10)

        self.phi_result = ctk.CTkLabel(self, text="")
        self.phi_result.grid(row=5, column=2, padx=10, pady=10)

        # CSV FILE NAME
        self.pathLabel = ctk.CTkLabel(self, text="OUTPUT CSV FILE NAME", font=("Arial", 16), text_color='white')
        self.pathLabel.grid(row=6, column =0, padx=10, pady=10)

        self.ePath = ctk.CTkEntry(self, placeholder_text='OUTPUT NAME')
        self.ePath.grid(row=6, column=1, padx=10, pady=10)

        self.path_result = ctk.CTkLabel(self, text="")
        self.path_result.grid(row=6, column=2, padx=10, pady=10)

        #BEGIN BUTTON
        self.begin_button = ctk.CTkButton(self, text="BEGIN", command=self.start_process)
        self.begin_button.grid(row=7, column=0, padx=10, pady=10)

        #KILL BUTTON
        self.kill_button = ctk.CTkButton(self, text='PANIC ABORT', command=self.kill)
        self.kill_button.grid(row=8, column=3, padx=10, pady=10)

        # DELETE WINDOW
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # TEXTBOX
        self.textbox = ctk.CTkTextbox(self, height=500, width=500, wrap="word")
        self.textbox.grid(row=0, column=4, padx=10, pady=10)

        #close button
        self.close_button = ctk.CTkButton(self, text='close', command=self.close)
        self.close_button.grid(row=9, column=4, padx=1, pady=1)

        self.abort_flag = threading.Event()
        self.process_thread = None

        self.kill_task = threading.Event()

    def start_process(self):
        global thread
        self.kill_task.clear()
        thread = threading.Thread(target=self.begin, daemon=True)
        thread.start()

    def read_steps(self):
        try:
            self.start = str(self.efStart.get())
            self.start_result.configure(text="START: " + self.start)
        except ValueError:
            self.start_result.configure(text="PLEASE ENTER A FLOATING POINT NUMBER")
            return
            # STOP VALUE
        try:
            self.stop = str(self.efStop.get())
            self.stop_result.configure(text="STOP: " + self.stop)
        except ValueError:
            self.stop_result.configure(text="PLEASE ENTER A FLOATING POINT NUMBER")
            return
            # STEP VALUE
        try:
            self.step = self.efStep.get()
            self.step_result.configure(text="STEP: " + str(self.step))
        except ValueError:
            self.step_result.configure(text="PLEASE ENTER A FLOATING POINT NUMBER")
            return
            # THETA VALUE
        try:
            self.theta = int(self.eTheta.get())
            self.theta_result.configure(text="THETA: " + str(self.theta))
        except ValueError:
            self.theta_result.configure(text="PLEASE ENTER A DECIMAL NUMBER")
            return
            # PHI VALUE
        try:
            self.phi = int(self.ePhi.get())
            self.phi_result.configure(text="PHI: " + str(self.phi))
        except ValueError:
            self.phi_result.configure(text="PLEASE ENTER A DECIMAL NUMBER")
            return
            # PATH
        try:
            self.path = str(self.ePath.get())
            self.path_result.configure(text="OUTPUT FILE NAME: " + str(self.path))
        except ValueError:
            self.path_result.configure(text="ENTER A PROPER PATH NAME")
            return
            # IF Bandwidth
        try:
            self.IFbandwidth = str(self.eIFB.get())
            self.IFB_result.configure(text="IF Bandwidth: " + self.IFbandwidth)
        except ValueError:
            self.IFB_result.configure(text="PLEASE ENTER A FLOATING POINT NUMBER")
            return

        # self.connect_to_controller()
        # time.sleep(0.1)
        # self.connect_to_vna()
        # time.sleep(0.1)
        # self.VNAwrite("STAR " + str(start) + "GHZ")
        # time.sleep(0.1)
        # self.VNAwrite("STOP " + str(stop) + "GHZ")
        # time.sleep(0.1)
        # self.VNAwrite("STEPSWP ON")
        # time.sleep(0.1)
        # # self.VNAwrite("IFBW " + str(self.IFbandwidth) + "HZ")
        # self.VNAwrite("STEP " + str(step))
        # time.sleep(0.1)
        #
        # for i in range(0, 300):
        #     if self.kill_task.is_set():
        #         print("ABORTED")
        #         return
        #     self.update_textbox("This is loop " + str(i))
        #     time.sleep(1)

        # for i in range(1, 361):
        # self.move_to_position(x=0, y=i)
        # time.sleep(3)
    def begin(self):
        self.read_steps()
        self.connect_to_controller()
        self.connect_to_vna()
        time.sleep(0.1)
        file_name = self.path

        with open(file=file_name, mode='w', newline='') as file:
            writer=csv.writer(file)
            writer.writerow(['Phi (degrees)', 'Theta (degrees)', 'Frequency (GHz)', 'S21 Magnitude (dB)'])
            self.move_to_position(x=0, y=0)
            time.sleep(20)
            phi_steps = 360 // self.phi + 1
            theta_steps = 90 // self.theta + 1

            for phi in range(phi_steps):
                current_position = self.get_position()
                self.update_textbox("MOVING TO POSITION: " + str(current_position[0]) + ", " + str(current_position[1] + self.phi))
                self.move_to_position(x=current_position[0], y=current_position[1] + self.phi)
                time.sleep(1)
                for theta in range(theta_steps):
                    current_position_1 = self.get_position()
                    self.update_textbox("MOVING TO POSITION: " + str(self.theta) + ", " + str(phi))
                    self.move_to_position(x=current_position_1[0] + self.theta, y=current_position_1[1])
                    time.sleep(1)
                    freqs=self.get_freq()
                    mags=self.get_mag()
                    for index in range(len(freqs)):
                        row = [current_position_1[1], current_position_1[0] + self.theta, freqs[index], mags[index]]
                        writer.writerow(row)
                    if theta == 89:
                        self.move_to_position(x=0, y=current_position_1)
                        time.sleep(20)




    def VNAwrite(self, msg):
        self.VNA.write(str(msg))

    def VNAread(self):
        return self.VNA.read()

    def VNAquery(self, msg):
        return self.VNA.query(str(msg) + "?")

    def connect_to_controller(self):
        try:

            self.serial_connection = serial.Serial(settings.COM_PORT, settings.BAUD_RATE, timeout=2)
            time.sleep(0.5)
            self.serial_connection.write(b'?')
            response = self.serial_connection.readline().decode('utf-8').strip()

            if response.startswith('<Idle|WPos:'):
                values = response.split(':')[1].split(',')
                if len(values) == 6:
                    x, y, z, a, b, c = values
                    self.update_textbox(f"Connected. Position at connection time is X{x} Y{y} A{a}\n")
                    #self.connect_button.configure(text='Connected', state=tk.DISABLED)

                else:
                    self.update_textbox("Invalid response format.")
            else:
                self.update_textbox("Failed to connect: Invalid response.")
        except serial.SerialException as e:
            self.update_textbox(f"Failed to connect: {str(e)}")

    def connect_to_vna(self):
        try:
            self.rm = pyvisa.ResourceManager()
            self.VNA = self.rm.open_resource("GPIB0::16::INSTR")
            self.update_textbox(self.VNA.query("*IDN?"))
        except pyvisa.VisaIOError:
            self.update_textbox("FAILED TO CONNECT TO VNA")

    def initialize_vna(self):
        self.VNA.write("S21")
        time.sleep(0.5)
        self.VNA.write("STAR " + str(self.start) + "GHZ")
        time.sleep(0.5)
        self.VNA.write("STOP " + str(self.stop) + "GHZ")
        time.sleep(0.5)
        self.VNA.write("STPSIZE " + str(self.step) + "HZ")
        time.sleep(0.5)
        self.VNA.write("IFBW "+ str(self.IFB_result) +"HZ")
        time.sleep(0.5)

    def move_to_position(self, x, y):
        self.serial_connection.write(f'G0 X{x} Y{y} Z0\n'.encode('utf-8'))  # Include default Z value




    def home(self):
        self.serial_connection.write(('$H\n').encode('utf-8'))

    def kill(self):
        self.serial_connection.close()
        self.VNA.close()
        self.update_textbox("PROCESS PANIC ABORTED")
        self.kill_task.set()

    def on_close(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Serial connection closed.")
        if self.VNA:
            self.VNA.close()
            print("VNA disconnected")

        self.destroy()

    def update_textbox(self, text):
        #self.textbox.delete("1.0", "end")  # Clear previous text
        #self.textbox.insert("end", text)  # Insert new text
        self.textbox.after(0, self.safe_update_textbox, text)

    def safe_update_textbox(self, text):
        if self.textbox.winfo_exists():
            self.textbox.delete("1.0", "end")  # Clear previous text
            self.textbox.insert("end", text)  # Insert new text

    def read_sparameters(self):
        return self.VNA.query("*IDN?")

    def close(self):
        self.destroy()

    def get_mag(self, chan="CHAN1"):
        """Returns a numpy array with the logarithmic magnitude values
        on the channel specified.

        Args:
            chan (str): String specifying the channel to get the values from
        """
        self.VNAwrite("FORM5;")  # Use binary format to output data
        self.VNAwrite(chan + ";")  # Select channel
        self.VNAwrite("LOGM;")  # Show logm values - TRY CALC:MEAS:FORM MLOG and CALC:MEAS:FORM PHAS
        # Might let you switch between the log mag and phase measurements. Should wrap this whole thing up ez pz!
        res = []



        aux = self.VNA.query_binary_values(
            "OUTPFORM;", container=tuple, header_fmt="hp"
        )  # Ask for the values from channel and format them as tuple
        for i in range(
                0, len(aux), 2
        ):  # Only get the first value of every data pair because the other is zero
            res.append(aux[i])
        return np.asarray(res)

    def get_freq(self):
        """Returns a numpy array with the values of frequency
        from the x-axis.
        """
        self.VNAwrite(
            "OUTPLIML;"
        )  # Asks for the limit test results to extract the stimulus components
        aux = []
        x = self.VNAread().split("\n")  # Split the string for each point



        for i in x:
            if i == "":
                break
            aux.append(
                float(i.split(",")[0])
            )  # Split each string and get only the first value as a float number
        return np.asarray(aux)

    def get_position(self):
        try:
            self.serial_connection.flushInput()
            self.serial_connection.write(('?').encode('utf-8'))
            time.sleep(0.1)
            response = self.serial_connection.readline().decode('utf-8').strip()

            if '<Idle|WPos:' in response:
                try:
                    values = response.split('|')[1].split(':')[1].split(',')
                    x, y, z, a = float(values[0]), float(values[1]), float(values[2]), float(values[3])
                    self.update_textbox(f"Current Position: X{x} Y{y} A{a}")
                    return float(x), float(y), float(a)
                except (IndexError, ValueError):
                    self.update_textbox("Invalid response format for position.")
                    return None, None, None
            else:
                self.update_textbox("Failed. Was the RESULTS file opened?")
                return None, None, None
        except serial.SerialException as e:
            self.update_textbox(f"Error in getting position: {str(e)}")
            return None, None, None
