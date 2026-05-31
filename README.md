# Custom Keyboard
## Releases
The built program can be found in github actions under the corresponding commit. There will be a file called "fireware.zip" that can be downloaded and flashed to the keyboard.
## Flashing Instructions
1. Connect the keyboard via a USB cable.
2. Double click the reset button on the keyboard (found below the rotary encoder) to enter bootloader mode. The keyboard should show up as a mass storage device on your computer.
3. Copy the "firmware.uf2" file from the downloaded release to the mass storage device to flash the keyboard. The storage device should automatically eject and the keyboard will reboot with the new firmware.
## Local Build Instructions
Source code is built in github actions using the ZMK firmware framework. To build the firmware locally, follow these steps:
1. Clone the ZMK repository using the following command:
```
git clone https://github.com/zmkfirmware/zmk.git
```
2. Set up the Zephyr SDK as described [here](https://docs.zephyrproject.org/3.5.0/develop/getting_started/index.html)
3. From the zmk directory, run the following commands to build the firmware, ensuring to replace "/path/to/this/repo/config" with the path to the config directory in this repository:
```
cd app
# To build the left side:
west build -p -b nice_nano@2.0.0 -- -DSHIELD="chirality_left nice_view_gem" -DZMK_CONFIG=/path/to/this/repo/config

# To build the right side:
west build -p -b nice_nano@2.0.0 -- -DSHIELD="chirality_right nice_view_gem" -DZMK_CONFIG=/path/to/this/repo/config
```
The built firmware file can be found at "/path/to/zmk/app/build/zephyr/zmk.uf2", and can be flashed with the [flash instructions](#flashing-instructions) above, treating "zmk.uf2" as "firmware.uf2".
For more information, see the [ZMK documentation](https://zmk.dev/docs/development/local-toolchain/setup/native) and [Zephyr documentation](https://docs.zephyrproject.org/3.5.0/develop/getting_started/index.html) 
