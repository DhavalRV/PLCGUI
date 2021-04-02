from pymodbus.client.sync import ModbusTcpClient
import time

ip = "10.24.0.2"

input_address = 0x400  # addressofinputX0
output_address = 0x500

with ModbusTcpClient(ip) as client:
    # read_discrete_inputsusesfunctioncode=2
    while True:
        response = client.read_discrete_inputs(1024, 16)  # readinputX0
        assert not response.isError()
        print(response.bits)

    # i = 0

    #     time.sleep(1)
    #     request = client.write_coil(output_address, i)
    #     i = i ^ 1
    #     print(i)
    #     assert not request.isError()


# #regs=c.read_holding_registers(0,1)
# bits = c.read_coils(0x400)
# print("reading register values")


# if bits:
#     print(str(bits))
# else:
#     print("error")

# print("write value to register")
# a=int(input())
# c.write_single_register(,a)
