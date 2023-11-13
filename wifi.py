# RGB Matrix Ticker Software > Wifi reconfiguration script
# By Joel Muscat (PuffCode)
# github.com/Puffball101961/matrixticker
# This software is made available under the GNU General Public License
# For more information, refer to the LICENSE file present in the root
# directory of the repository.

import time
import subprocess

from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import requests

from PIL import Image, ImageDraw


# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32 # height of the display
options.cols = 128 # width of the display
options.parallel = 1
options.hardware_mapping = 'adafruit-hat-pwm'  # If you have an Adafruit HAT: 'adafruit-hat'
#options.pixel_mapper_config = "Rotate:180" # Rotate 180 degrees if required.
options.led_rgb_sequence = "RBG" # Change to RGB if your matrix has led colors swapped

matrix = RGBMatrix(options = options)

splash = Image.new('RGBA', (128,32))
draw = ImageDraw.Draw(splash)
icon = Image.open(f"net_setup.png")
icon.thumbnail((128,32))
splash.paste(icon, (0,0))
matrix.SetImage(splash.convert('RGB'))
subprocess.call("sudo wifi-connect --portal-ssid 'MatrixTicker Setup'", shell=True)
matrix.Clear()
splash = Image.new('RGBA', (128,32))
draw = ImageDraw.Draw(splash)
icon = Image.open(f"checking.png")
icon.thumbnail((128,32))
splash.paste(icon, (0,0))
matrix.SetImage(splash.convert('RGB'))
try:
    res = requests.get("https://google.com")
    if res.status_code == 200:
        connected = True
except requests.ConnectionError:
    connected = False