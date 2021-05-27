import pysoem
import netifaces


def get_nicid(ip):
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        try:
            id = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]["addr"]
            if id == ip:
                return interface
        except:
            pass


nic_id = get_nicid("10.39.0.117")
full_id = str(f"\\Device\\NPF_{nic_id}")
# print(full_id)

master = pysoem.Master()
master.open(full_id)

if master.config_init() > 0:
    device_foo = master.slaves[0]
    device_bar = master.slaves[1]
else:
    print("No device found")
