from meer_tec import TEC, USB, XPort

import h5py
import numpy as np
from configparser import ConfigParser

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import WritePrecision

import datetime
import time

class Monitoring():

    def __init__(self) -> None:

        self.config = ConfigParser() 
        self.config.read("TEC.ini")

        self.load_TEC()
        self.setup_influx()
        

    def load_TEC(self):
        self.TEC_COM = self.config['USB']['COM']
        self.usb = USB(self.TEC_COM)
        self.tec1 = TEC(self.usb , 0)
    
    def setup_influx(self):
        influxdb_conf = self.config["influxdb"] 
        self.influxdb_client = InfluxDBClient(
            url=f"{influxdb_conf['host']}:{influxdb_conf['port']}", token=influxdb_conf["token"], org=influxdb_conf["org"]
        )
        self.has_influx = True
        self.influxdb_org: str = influxdb_conf["org"]
        self.influxdb_bucket: str = influxdb_conf["bucket"]
        self.device: str = influxdb_conf['device']
        self.influx_write_api = self.influxdb_client.write_api(write_options=SYNCHRONOUS)

    def read_temp(self):
        self.temp_read = self.tec1.object_temperature_ch1
        return self.temp_read
    
    def read_curr(self):
        self.curr_read = self.tec1.actual_output_current_ch1
        return self.curr_read

if __name__  == "__main__":
    do_monitor = True
    monitoring = Monitoring()
    while do_monitor:
        if monitoring.has_influx:
            # Read temp and current from TEC
            temp = monitoring.read_temp()
            curr = monitoring.read_curr()
            utc_t_now = datetime.utcnow()

            # Push data to influxdb and then to Grafana
            temp_val = Point('Temperature Measure').tag('Device', monitoring.device).field('Temperature', temp).time(utc_t_now, WritePrecision.MS)
            curr_val = Point('Current Measure').tag('Device', monitoring.device).field('Current', curr).time(utc_t_now, WritePrecision.MS)
            monitoring.influx_write_api.write(monitoring.influxdb_bucket, monitoring.influxdb_org, temp_val)
            monitoring.influx_write_api.write(monitoring.influxdb_bucket, monitoring.influxdb_org, curr_val)
    # temp = []

    # tec.coarse_temp_ramp_ch1 = 0.02

    # tec.target_object_temperature = 24

    # for i in range(10):
    #     tec.target_object_temperature = 24+0.3*i
    #     temp.append(tec.object_temperature_ch1)
    #     time.sleep(0.5)

    # print(temp)
