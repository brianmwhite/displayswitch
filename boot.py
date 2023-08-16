# SPDX-FileCopyrightText: 2021 Kattni Rembor for Adafruit Industries
# SPDX-License-Identifier: MIT
"""
CircuitPython Essentials Storage CP Filesystem boot.py file
"""
import time
import board
import digitalio
import storage
import neopixel

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)

potentiometer_switch = digitalio.DigitalInOut(board.A1)
potentiometer_switch.direction = digitalio.Direction.INPUT
potentiometer_switch.pull = digitalio.Pull.UP

# Turn the NeoPixel blue for one second to indicate when to press the boot button.
pixel.fill((255, 255, 255))
time.sleep(1)

if potentiometer_switch.value:
    storage.remount("/", readonly=True)
else:
    storage.remount("/", readonly=False)
