from meer_tec import TEC, USB, XPort

usb = USB("COM10")
tec1 = TEC(usb , 0)

tec1.coarse_temp_ramp_ch1 = 0.02

tec1.target_object_temperature = 150