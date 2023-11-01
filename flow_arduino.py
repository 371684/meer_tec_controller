import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import serial
import time
import h5py
from datetime import datetime

rm = pyvisa.ResourceManager()

class flow_con ():

    def __init__(self) -> None:
        add_A = 'COM5'
        self.load_ard(add_A)


    def load_ard(self , addr):
        corr_resp = 'Flow controller Arduino ready.\r\n'
        for i in range(3):
            try:
                self.ard = serial.Serial(port = addr , baudrate= 115200)
                time.sleep(1)
                self.ard.write(bytes('?','utf-8'))
                resp = self.ard.readline().decode('utf-8')
                if resp == corr_resp:
                    print(corr_resp)
                    print("The correct address is:", addr)
                    return self.ard
                    break
                else:
                    rm.close(addr)
            except:
                print("Not this address")
    
    def read_flow(self):
        self.ard.write(bytes('f','utf-8'))
        flow = float(self.ard.readline().decode('utf-8'))
        return flow
    
    def read_set(self):
        self.ard.write(bytes('o','utf-8'))
        set_volt = float(self.ard.readline().decode('utf-8'))
        return set_volt
    
    def set_volt(self, val):
        com = 's' +str(val)
        self.ard.write(bytes(com,'utf-8'))
        return com

if __name__  == "__main__":
    floward = flow_con()
    flow_val = floward.readflow()
    print('the current flow rate is :' + str(flow_val) + ' sccm' )
    set_val = floward.read_set()
    print('the set flow rate is :' + str(set_val) + ' sccm' )
