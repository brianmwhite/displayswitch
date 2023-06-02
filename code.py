import board
from adafruit_neokey.neokey1x4 import NeoKey1x4

i2c_bus = board.STEMMA_I2C()

neokey = NeoKey1x4(i2c_bus, addr=0x30)

key_0_state = False
key_1_state = False
key_2_state = False
key_3_state = False

while True:
    if not neokey[0] and key_0_state:
        key_0_state = False
        neokey.pixels[0] = 0x0
    if not neokey[1] and key_1_state:
        key_1_state = False
        neokey.pixels[1] = 0x0
    if not neokey[2] and key_2_state:
        key_2_state = False
        neokey.pixels[2] = 0x0
    if not neokey[3] and key_3_state:
        key_3_state = False
        neokey.pixels[3] = 0x0

    if neokey[0] and not key_0_state:
        print("Button A")
        neokey.pixels[0] = 0xFF0000
        key_0_state = True

    if neokey[1] and not key_1_state:
        print("Button B")
        neokey.pixels[1] = 0xFFFF00
        key_1_state = True

    if neokey[2] and not key_2_state:
        print("Button C")
        neokey.pixels[2] = 0x00FF00
        key_2_state = True

    if neokey[3] and not key_3_state:
        print("Button D")
        neokey.pixels[3] = 0x00FFFF
        key_3_state = True
