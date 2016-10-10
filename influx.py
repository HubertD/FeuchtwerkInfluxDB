import can
from influxdb import InfluxDBClient
from time import gmtime, strftime

client = InfluxDBClient("10.42.102.174", 8086, "collectd", "secretPassword", "collectd")

def report_feuchtwerk(node_name, data):
    temp_raw = data[2] << 8 | data[1]
    hum_raw = data[4] << 8 | data[3]
    temperature = (temp_raw * 0.0025177) - 40

    sub = (temperature - 10) * 0.15
    if sub > 0:
        temperature -= min(3, sub)

    humidity = hum_raw * 0.00152590219

    dt = strftime("%Y-%m-%d %H:%M:%SZ", gmtime())

    json = [
        {
            "measurement": "feuchtwerk",
            "tags": {
                "host": node_name,
                "type": "temperature"
            },
            "time": dt,
            "fields": {
                "value": temperature
            }
        },
        {
            "measurement": "feuchtwerk",
            "tags": {
                "host": node_name,
                "type": "humidity"
            },
            "time": dt,
            "fields": {
                "value": humidity
            }
        }
    ]

    print(json)

    client.write_points(json)



report_feuchtwerk("test", [0,0,0,0,0])
exit()

bus = can.interface.Bus("can0", bustype='socketcan_native')

while True:
    msg = bus.recv()
    if msg.arbitration_id==0x211001: # feuchtwerk1_01
        report_feuchtwerk("feuchtwerk01", msg.data)
    if msg.arbitration_id == 0x212001:  # feuchtwerk2_01
        report_feuchtwerk("feuchtwerk02", msg.data)
    if msg.arbitration_id == 0x213001:  # feuchtwerk3_01
        report_feuchtwerk("feuchtwerk03", msg.data)
