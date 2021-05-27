import netifaces
import pprint

# pp = pprint.PrettyPrinter(indent=4)
# # pp.pprint(netifaces.interfaces())
# pp.pprint(
#     netifaces.ifaddresses("{67D13274-78CE-47A1-AD7F-0BACA66C9E42}")[netifaces.AF_INET][
#         0
#     ]["addr"]
# )
def get_nicaddress(ip):
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        try:
            address = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]["addr"]
            if address == ip:
                print(interface)
                return
        except:
            pass


if __name__ == "__main__":
    get_nicaddress("10.39.0.117")