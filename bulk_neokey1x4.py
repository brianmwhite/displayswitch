# example from: 
# https://github.com/Neradoc/circuitpython-sample-scripts/blob/997cf54482256e37f11b9acfd5b79a5369493bd3/seesaws/bulk_neokey1x4.py
# from https://github.com/Neradoc/circuitpython-sample-scripts
# license = unlicense
# https://github.com/Neradoc/circuitpython-sample-scripts/blob/main/LICENSE

import board
import digitalio
from adafruit_neokey.neokey1x4 import NeoKey1x4
import time

i2c_bus = board.STEMMA_I2C()
neokey = NeoKey1x4(i2c_bus, addr=0x30)

# button names are arbitrary
BUTTON_A = const(1 << 4)
BUTTON_B = const(1 << 5)
BUTTON_C = const(1 << 6)
BUTTON_D = const(1 << 7)
button_mask = BUTTON_A|BUTTON_B|BUTTON_C|BUTTON_D

# set the buttons to input, pull up
neokey.pin_mode_bulk(button_mask, neokey.INPUT_PULLUP)

# past state of the buttons to detect changes
buttons_pressed_past = button_mask
start_time = 0.0
end_time = 0.0

while True:
    # get the bitmask of the buttons state
    # this resets the interrupt pin (to HIGH)
    buttons_pressed = neokey.digital_read_bulk(button_mask)

    if buttons_pressed_past != buttons_pressed:

        # buttons that just got pressed
        if buttons_pressed & BUTTON_A == 0 and buttons_pressed_past & BUTTON_A:
            print("Button A")
            # start = millis()
            start_time = time.monotonic()
        if buttons_pressed & BUTTON_B == 0 and buttons_pressed_past & BUTTON_B:
            print("Button B")
            start_time = time.monotonic()
        if buttons_pressed & BUTTON_C == 0 and buttons_pressed_past & BUTTON_C:
            print("Button C")
            start_time = time.monotonic()
        if buttons_pressed & BUTTON_D == 0 and buttons_pressed_past & BUTTON_D:
            print("Button D")
            start_time = time.monotonic()

        # buttons that just got released
        if buttons_pressed_past & BUTTON_A == 0 and buttons_pressed & BUTTON_A:
            end_time = time.monotonic()
            print(f"Button A Released after {end_time - start_time}")
        if buttons_pressed_past & BUTTON_B == 0 and buttons_pressed & BUTTON_B:
            end_time = time.monotonic()
            print(f"Button B Released after {end_time - start_time}")
        if buttons_pressed_past & BUTTON_C == 0 and buttons_pressed & BUTTON_C:
            end_time = time.monotonic()
            print(f"Button C Released after {end_time - start_time}")
        if buttons_pressed_past & BUTTON_D == 0 and buttons_pressed & BUTTON_D:
            end_time = time.monotonic()
            print(f"Button D Released after {end_time - start_time}")

    # save the state
    buttons_pressed_past = buttons_pressed