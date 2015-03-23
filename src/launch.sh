#!/bin/bash

echo '\033[36m\033[1mStarting SailBOT...\033[0m\033[39m'

echo '\033[36m\033[1mConfiguring GPSD...\033[0m\033[39m'
sudo killall gpsd
sudo gpsd /dev/ttyUSB0 -F /var/run/gpsd.sock

echo '\033[36m\033[1mCreating GPSD TCP Socket...\033[0m\033[39m'
sudo python "modules/pgps.py" &

echo '\033[36m\033[1mLaunching main program...\033[0m\033[39m'
sudo python3 main.py