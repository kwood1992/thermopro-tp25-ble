"""Constants for the ThermoPro TP25 BLE integration."""

"""Handshake / start streaming commands."""
HANDSHAKE_COMMANDS = [
    bytes.fromhex("01098a7a13b73ed68b67c2a0"),
    bytes.fromhex("410041"),
    bytes.fromhex("28040b43f60373"),
    bytes.fromhex("20010c2d"),
    bytes.fromhex("2306018218990588ea"),
    bytes.fromhex("2306020a074000007c"),
    bytes.fromhex("23060300ffffffff28"),
    bytes.fromhex("23060400ffffffff29"),
]

"""BLE Characteristics."""
CMD_CHAR_UUID = "1086fff1-3343-4817-8bb2-b32206336ce8"   # Command characteristic
DATA_CHAR_UUID = "1086fff2-3343-4817-8bb2-b32206336ce8"  # Data characteristic

NUM_PROBES = 6
