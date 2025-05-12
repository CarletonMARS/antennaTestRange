import pyvisa
import time
import numpy as np


class VNAController:
    def __init__(self, resource_str: str):
        self.resource_str = resource_str
        self.rm = None
        self.VNA = None

    def connect(self):
        """Opens the VISA resource and checks for identity"""
        self.rm = pyvisa.ResourceManager()
        self.VNA = self.rm.open_resource(self.resource_str)
        idn = self.VNA.query("*IDN?")
        return idn.strip()

    def write(self, cmd: str):
        """Sends SCPI Comment without query"""
        if not self.VNA:
            raise RuntimeError("VNA not connected")
        self.VNA.write(cmd)
        time.sleep(0.1)

    def query(self, cmd: str) -> str:
        """Sends cmd? and returns response as string"""
        if not self.VNA:
            raise RuntimeError("VNA not connected")
        return self.VNA.query(cmd)

    def select_sparam(self, sparam: str):
        """select S11, S21, etc."""
        self.write(sparam)

    def read_trace(self, channel: str = "CHAN1") -> (np.ndarray, np.ndarray):
        """Returns (freq_GHz, mag_dB) arrays
            Defaults Channel 1 Readings,
            Assumes OUTPLIML, FORM5, OUTPFORM
        """

        # frequency axis
        self.write("OUTPLIML")
        raw = self.VNA.read().splitlines()
        freqs = np.array([float(line.split(',')[0]) for line in raw if line])

        self.write("FORM5;")
        self.write(f"{channel};")

        vals = self.VNA.query_binary_values("OUTPFORM;", container=list, header_fmt="hp")

        mags = np.array(vals[0::2])
        return freqs / 1e9, mags

    def reset(self):
        """Full reset VNA"""
        self.write("*RST")
        time.sleep(0.1)

    def close(self):
        """Close session"""
        if self.VNA:
            self.VNA.control_ren(0)
        if self.rm:
            self.rm.close()
