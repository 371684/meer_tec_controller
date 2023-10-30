from meer_tec import TEC, USB, XPort 
import time

usb = USB("COM4")
tec = TEC(usb, 0)

temp = []

tec.coarse_temp_ramp_ch1 = 0.02

tec.target_object_temperature = 24

for i in range(10):
    tec.target_object_temperature = 24+0.3*i
    temp.append(tec.target_object_temperature)
    time.sleep(1)

print(temp)
