import os
import ssl
import time

import adafruit_requests
import analogio
import board
import socketpool
import storage
import wifi
from adafruit_neokey.neokey1x4 import NeoKey1x4
from digitalio import DigitalInOut, Direction, Pull


# def log_error_messages(message):
#     try:
#         with open("/error_log.txt", "a") as error_log:
#             print(message)
#             error_log.write(f"{message}\n")
#             error_log.flush()
#     except RuntimeError as re:
#         print(re)
#         # ignore
#         pass
#     except Exception as e:
#         print(e)

# CircuitPython code for the Adafruit NeoKey 1x4 and QT Py ESP32-S3
# When a button is pressed this code will send a HTTP get request to a web service that switches the hdmi input for a monitor
# when the neokey[0] button is pressed it will switch buttons 1,2,3 to a different set of hdmi inputs
# there are 9 possible hdmi that can be switched to
# continuing to press button 0 will cycle through the 9 hdmi inputs, 3 at a time on buttons 1,2,3
# when the neokey[0] button is pressed again it will switch buttons 1,2,3 to a different set of hdmi inputs
# each hdmi input will have a different color assigned to the neokey.pixels[1-3] buttons

web_service_base_url = f"http://192.168.7.97:5015/hdmiswitch"

# a collection of hdmi input variables that has 9 entries. each entry should have two values a string and a color
# the string is the hdmi input that will be sent to the web service
# the color is the color that will be assigned to the neokey.pixels[1-3] buttons
# the color is a hex value that is in the format 0xRRGGBB

hdmi_inputs = [
    {"input": "macstudio", "color": 0x0000FF},
    {"input": "macbook", "color": 0xFFB703},
    {"input": "nintendoswitch", "color": 0xFF0000},
    {"input": "roku", "color": 0x8800FF},
    {"input": "macmini", "color": 0xFF2800},
    {"input": "snes", "color": 0x32FFFF},
    {"input": "ipad", "color": 0x00FF00},
    {"input": "rpi", "color": 0xFF004C},
    {"input": "extra", "color": 0x858585},
]

i2c_bus = board.STEMMA_I2C()
neokey = NeoKey1x4(i2c_bus, addr=0x30)

# set the brightness range of the pixels
MIN_BRIGHTNESS = 0.02
MAX_BRIGHTNESS = 0.8

# set the photocell ranges of values
MAX_PHOTOCELL_VALUE = 2000
MIN_PHOTOCELL_VALUE = 0

# setup potentiometer switch
potentiometer_switch = DigitalInOut(board.A1)
potentiometer_switch.direction = Direction.INPUT
potentiometer_switch.pull = Pull.UP
photocell = analogio.AnalogIn(board.A3)

key_0_state = False
key_1_state = False
key_2_state = False
key_3_state = False

current_collection_set = 0

potentiometer_switch_state_changed = False
potentiometer_switch_last_state = potentiometer_switch.value


# scale pixel brightness based on photocell value
# photocell value is between 0 and 3000
# pixel brightness is between 0.02 and 1
# pixel brightness will be 0.02 when photocell value is 0
# pixel brightness will be 1 when photocell value is 3000
# pixel brightness will be 0.51 when photocell value is 1500
def scale_brightness(photocell_value):
    actual_percent = (photocell_value / MAX_PHOTOCELL_VALUE) * (
        MAX_BRIGHTNESS - MIN_BRIGHTNESS
    ) + MIN_BRIGHTNESS
    # round to nearest tenth
    # rounded_percent = round(actual_percent, 1)
    rounded_percent = actual_percent

    if rounded_percent > MAX_BRIGHTNESS:
        rounded_percent = MAX_BRIGHTNESS
    elif rounded_percent < MIN_BRIGHTNESS:
        rounded_percent = MIN_BRIGHTNESS

    return rounded_percent


# set brightness
# neokey.pixels.brightness = scale_brightness(photocell.value)
neokey.pixels.brightness = 0.8


# turn the first pixel red to indicate that the device is booting up
neokey.pixels[0] = 0xFF0000

print("Connecting to WiFi...")
wifi.radio.connect(
    os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD")
)
print("Connected to WiFi!")
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

# turn the first pixel off to indicate that the device is done booting up and has connected to wifi
neokey.pixels[0] = 0x0


def change_button_collection_colors():
    global current_collection_set
    print(f"current_collection_set (start): {current_collection_set}")
    if current_collection_set >= len(hdmi_inputs):
        current_collection_set = 0
    print(f"current_collection_set (after len check): {current_collection_set}")
    for i in range(0, 3):
        neokey.pixels[i + 1] = hdmi_inputs[current_collection_set + i]["color"]
        print(
            f"button: {i+1} to input {hdmi_inputs[current_collection_set + i]['input']}"
        )

    print(f"photocell = {photocell.value}")


def send_webservice_request(button_number):
    global current_collection_set
    print(f"current_collection_set: {current_collection_set}")
    item_number = current_collection_set + (button_number - 1)
    print(f"button_number: {button_number}")
    print(f"item_number: {item_number}")
    # log_error_messages(f"Sending request to {web_service_base_url}/{hdmi_inputs[item_number]['input']}")
    print(
        f"Sending request to {web_service_base_url}/{hdmi_inputs[item_number]['input']}"
    )

    # set the first pixel to white to indicate that the request is being sent
    neokey.pixels[0] = 0xFFFFFF

    try:
        requests.get(f"{web_service_base_url}/{hdmi_inputs[item_number]['input']}")
        # set the first pixel to off to indicate that the request is done being sent
        neokey.pixels[0] = 0x0
    except Exception as e:
        neokey.pixels[0] = 0xFF0000
        # log_error_messages(e)
        print(e)


def turn_off_buttons():
    global current_collection_set
    global key_0_state
    global key_1_state
    global key_2_state
    global key_3_state

    neokey.pixels[0] = 0x0
    neokey.pixels[1] = 0x0
    neokey.pixels[2] = 0x0
    neokey.pixels[3] = 0x0

    key_0_state = False
    key_1_state = False
    key_2_state = False
    key_3_state = False

    current_collection_set = 0

    while potentiometer_switch.value:
        pass

    change_button_collection_colors()


# main loop

change_button_collection_colors()

BRIGHTNESS_INTERVAL_SECONDS = 0.1
last_brightness_check = None
prior_brightness = None

# check if the switch is off when starting up, otherwise leds will be on
# but nothing will happen when you press a button
if potentiometer_switch.value:
    print("switch off, turning off pixels")
    turn_off_buttons()

while True:
    # add a short sleep to prevent the device from locking up
    # time.sleep(0.07)
    if potentiometer_switch_last_state != potentiometer_switch.value:
        potentiometer_switch_last_state = potentiometer_switch.value
        potentiometer_switch_state_changed = True
    else:
        potentiometer_switch_state_changed = False

    if not potentiometer_switch.value:
        # check the photocell value every 1 second and adjust the brightness of the pixels
        # this should be non blocking and continue to allow the buttons to be pressed
        # if the photocell value drops to min_photocell_value then set the brightness to min_brightness
        # but decrease the brightness gradually in steps of 0.1

        # if (
        #     last_brightness_check is None
        #     or time.monotonic() > last_brightness_check + BRIGHTNESS_INTERVAL_SECONDS
        # ):
        #     new_brightness = scale_brightness(photocell.value)

        #     change_brightness = False

        #     if new_brightness != prior_brightness:
        #         neokey.pixels.brightness = new_brightness
        #         prior_brightness = new_brightness
        #         change_brightness = True

        #     last_brightness_check = time.monotonic()
        #     print(f"photocell = {photocell.value} | brightness = {new_brightness} | change_brightness = {change_brightness}")

        # # every one minute set the first neopixel to a dark gray for a partial second to make sure things stay running
        # if time.monotonic() % 60 < 0.01:
        #     neokey.pixels[0] = 0x111111
        # else:
        #     neokey.pixels[0] = 0x0

        # debouncing code to prevent multiple button presses
        if not neokey[0] and key_0_state:
            key_0_state = False
            neokey.pixels[0] = 0x0
        if not neokey[1] and key_1_state:
            key_1_state = False
            # neokey.pixels[1] = 0x0
        if not neokey[2] and key_2_state:
            key_2_state = False
            # neokey.pixels[2] = 0x0
        if not neokey[3] and key_3_state:
            key_3_state = False
            # neokey.pixels[3] = 0x0

        if neokey[0] and not key_0_state:
            print("Button 0")
            neokey.pixels[0] = 0xFFFFFF
            key_0_state = True
            current_collection_set += 3
            change_button_collection_colors()

        if neokey[1] and not key_1_state:
            print("Button 1")
            send_webservice_request(1)
            key_1_state = True

        if neokey[2] and not key_2_state:
            print("Button 2")
            send_webservice_request(2)
            key_2_state = True

        if neokey[3] and not key_3_state:
            print("Button 3")
            send_webservice_request(3)
            key_3_state = True
    # if the potentiometer switch is turned off then turn off all the buttons
    # only if the state just changed, we don't want to continuously turn them off
    elif potentiometer_switch.value and potentiometer_switch_state_changed:
        print("switch off, turning off pixels")
        turn_off_buttons()
