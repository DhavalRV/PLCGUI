plc_address = {
    "X0": 0x400,
    "X1": 0x401,
    "X2": 0x402,
    "X3": 0x403,
    "X4": 0x404,
    "X5": 0x405,
    "X6": 0x406,
    "X7": 0x407,
    "Y0": 0x500,
    "Y1": 0x501,
    "Y2": 0x502,
    "Y3": 0x503,
    "Y4": 0x504,
    "Y5": 0x505,
    "Y6": 0x506,
    "Y7": 0x507,
    "Y10": 0x508,
    "Y11": 0x509,
    "Y12": 0x50A,  # 510
    "Y13": 0x50B,  # 511
    "Y14": 0x50C,  # 512
    "Y15": 0x50D,  # 513
    "Y16": 0x50E,  # 514
    "Y17": 0x50F,  # 515
    "Y20": 0x510,  # 516
    "Y21": 0x511,  # 517
    "Y22": 0x512,  # 518
    "Y23": 0x513,  # 519
    "Y24": 0x514,  # 520
    "Y25": 0x515,  # 521
    "Y26": 0x516,  # 522
    "Y27": 0x517,  # 523
    "Y30": 0x518,
    "Y31": 0x519,
    "Y32": 0x51A,
    "Y33": 0x51B,
    "Y34": 0x51C,
    "M0": 0x800,
    "M1": 0x801,
    "M2": 0x802,
    "M3": 0x803,
    "M4": 0x804,
    "M5": 0x805,
    "M6": 0x806,
    "M7": 0x807,
    "M8": 0x808,
    "M9": 0x809,
    "M10": 0x810,
    "M11": 0x811,
    "M12": 0x812,
    "M13": 0x813,
    "M14": 0x814,
    "M15": 0x815,
    "M16": 0x816,
    "M17": 0x817,
    "M18": 0x818,
    "M19": 0x819,
    "M256": 0x900,
}


def get_address(port):
    address = plc_address[port]
    return address


if __name__ == "__main__":
    h = get_address("X0")
    print(h)