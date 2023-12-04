from meer_tec import TEC, USB, XPort
from flow_arduino import flow_con

import h5py
import numpy as np
from configparser import ConfigParser

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.domain.write_precision import WritePrecision

from datetime import datetime
import time

class Monitoring():

    def __init__(self) -> None:

        self.config = ConfigParser() 
        self.config.read("TEC.ini")

        self.load_TEC()
        self.setup_influx()
        self.flow_ard = flow_con()
        

    def load_TEC(self):
        self.TEC_COM = self.config['USB']['COM1']
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
        self.device: str = influxdb_conf['device1']
        self.influx_write_api = self.influxdb_client.write_api(write_options=SYNCHRONOUS)

    def read_temp(self):
        self.temp_read = self.tec1.object_temperature_ch1
        return self.temp_read
    
    def read_curr(self):
        self.curr_read = self.tec1.actual_output_current_ch1
        return self.curr_read
    
    def read_settemp(self):
        self.settemp_read = self.tec1.target_object_temperature
        return self.settemp_read
    
    def read_voltage(self):
        self.voltage_read = self.tec1.actual_output_voltage_ch1
        return self.voltage_read


if __name__  == "__main__":
    do_monitor = True
    monitoring = Monitoring()
    while do_monitor:
        if monitoring.has_influx:
            # Read temp and current from TEC
            temp = monitoring.read_temp()
            time.sleep(0.5)

            curr = monitoring.read_curr()
            time.sleep(0.5)

            set_temp = monitoring.read_settemp()
            time.sleep(0.5)

            volt = monitoring.read_voltage()
            time.sleep(0.5)

            # Read the flow speed from flow controller
            flow = monitoring.flow_ard.read_flow()
            time.sleep(0.5)

            set_flow = monitoring.flow_ard.read_set()
            time.sleep(0.5)

            utc_t_now = datetime.utcnow()

            # Push data to influxdb and then to Grafana
            temp_val = Point('UV_Cavity_TEC').tag('name', monitoring.device).field('Temperature', temp).time(utc_t_now, WritePrecision.MS)
            curr_val = Point('UV_Cavity_TEC').tag('name', monitoring.device).field('Current', curr).time(utc_t_now, WritePrecision.MS)
            set_val = Point('UV_Cavity_TEC').tag('name', monitoring.device).field('set_temperature', set_temp).time(utc_t_now, WritePrecision.MS)
            volt_val = Point('UV_Cavity_TEC').tag('name', monitoring.device).field('voltage', volt).time(utc_t_now, WritePrecision.MS)
            flow_val = Point('UV_Cavity_TEC').tag('name', 'flow_controller').field('flow', flow).time(utc_t_now, WritePrecision.MS)
            flow_set_val = Point('UV_Cavity_TEC').tag('name', 'flow_controller').field('set_flow', set_flow).time(utc_t_now, WritePrecision.MS)

            monitoring.influx_write_api.write(monitoring.influxdb_bucket, monitoring.influxdb_org, temp_val)
            monitoring.influx_write_api.write(monitoring.influxdb_bucket, monitoring.influxdb_org, curr_val)
            monitoring.influx_write_api.write(monitoring.influxdb_bucket, monitoring.influxdb_org, set_val)
            monitoring.influx_write_api.write(monitoring.influxdb_bucket, monitoring.influxdb_org, volt_val)
            monitoring.influx_write_api.write(monitoring.influxdb_bucket, monitoring.influxdb_org, flow_val)
            monitoring.influx_write_api.write(monitoring.influxdb_bucket, monitoring.influxdb_org, flow_set_val)
            time.sleep(10)

