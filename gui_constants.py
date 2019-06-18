window_title = "CAN-FD Sniffer"
window_size = "820x200"
rx_textbox_height = 10
rx_textbox_width = 50
tx_msg_width = 50

mode_dict = {
    "NORMAL_MODE": 0x00,
    "SLEEP_MODE":  0x01,
    "INTERNAL_LOOPBACK_MODE":  0x02,
    "LISTEN_ONLY_MODE":  0x03,
    "CONFIGURATION_MODE":  0x04,
    "EXTERNAL_LOOPBACK_MODE":  0x05,
    "CLASSIC_MODE":  0x06,
    "RESTRICTED_MODE":  0x07,
    "INVALID_MODE":  0xFF
}

dlc_dict = {
    "CAN_DLC_0":  0,
    "CAN_DLC_1":  1,
    "CAN_DLC_2":  2,
    "CAN_DLC_3":  3,
    "CAN_DLC_4":  4,
    "CAN_DLC_5":  5,
    "CAN_DLC_6":  6,
    "CAN_DLC_7":  7,
    "CAN_DLC_8":  8,
    "CAN_DLC_12":  9,
    "CAN_DLC_16":  10,
    "CAN_DLC_20":  11,
    "CAN_DLC_24":  12,
    "CAN_DLC_32":  13,
    "CAN_DLC_48":  14,
    "CAN_DLC_64":  15
}
