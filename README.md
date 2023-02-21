# RGB Matrix Ticker
RGB Matrix Crypto and Stock Ticker based on a Raspberry Pi

I'm not a pro 3d modeller or programmer so pls don't attack me :)
This project was a part of hackclub.com 's Winter Hardware Wonderland Program.

This Project is not 100% complete, and is not foolproof. You will need some knowledge and common sense to get it working.
I am planning to refine the process when I have time to work on it.

## Components Required
- 2x 64x32 RGB Matrix Panels (2.5mm Pitch) (The Waveshare branded panels come with all the wires you need for them so thats what I recommend purchasing)
- Raspberry Pi 3A+ (Will work with a 3B(+), and Pi 4. May work with a Pi Zero W, however it is untested)
- Heatsink for the Pi
- 16GB+ Micro SD Card, a good quality one from a known brand like SanDisk is a good idea.
- 5v 10A Power Supply (Ensure that you get the correct input voltage for your country)
- 3 Pin Power Connector with switch and fuse for the PSU + Appropriate power cable. My 3d model uses the variant with no screw holes, just small clips.
- Adafruit RGB Matrix HAT (Optional, if not using you will need to directly wire the panels to the Pi and tweak a couple lines of code)
- Micro USB Cable
- 2 60mm 5v Fans (I would actually recommend running 12v fans at 5v, as the 5v fans are quite loud) (Technically optional, however the PSU can get quite hot under load)
- DC Motor PWM Controller (Optional, if using loud 5v fans)
- Miscellaneous wires
- Spade connectors that fit your PSU

## Equipment Needed
- Soldering Iron
- 3D Printer (Or other way to fabricate the case)
- Super Glue (To Assemble the 3D Printed case)

## Brief Assembly Guide
Preface: Before you even consider making this you should have at least a basic knowledge of electronics and using raspberry pis.
1: 3D Print/ Fabricate the case and assemble.
2: Solder spade connectors to the fan wires.
3: Remove the Type A end from the micro usb cable (the end that doesnt plug into the Pi) and solder spade connectors.
4: If your Matrix Panel power cables don't have spade connectors, solder them on.
5: Install the panels into the front of the case, and screw them in. Ensure that the arrows on the back of the panels are pointing right (looking from the back)
6: Install Fans, I recommend having the fan near the Pi as an intake and the other fan as an exhaust.
7: If using a PWM fan controller, wire it to the PSU and fans.
8: Screw the Pi into the raised portions of the back of the case, and attach the Matrix Controller HAT (if using one)
9: Install the Power Connector into the left side, it should click in. If it doesn't click in try filing the ridges of the case down a touch.
10: Connect all spade connectors to the screw terminals on the PSU. BE CAREFUL!! Ensure you connect the wires to their correct terminals to avoid the MAGIC SMOKE!
11: Connect the 2 panels together using the provided ribbon cable, then connect the panel closest to the pi to the HAT, or directly wire it to the Pi.
12: Flash the micro sd card with raspberry pi os lite. I recommend using Raspberry Pi Imager as you can easily set up WiFi and SSH configs.
13: Clone this repo and run the code.
14: Hope it works.

Hzeller's repository for driving RGB Matrix Panels is very helpful for troubleshooting your build. Make sure to check it out if you are having issues.
If you can't find the solution to the problem you are having open an issue and I'll try my best to help you out.

## Contributing
I will be welcoming improvements and extra features to the code. Open a PR with your proposed changes and I will have a look.

## License
This Open Source software is distributed under the GNU GPLv3 license. You may modify this code however you like, and distribute it. Source code must be made available if you are distributing. You are not allowed to create closed source software based on this code. More info can be found at this website: https://choosealicense.com/licenses/gpl-3.0/

