# RGB Matrix Ticker Software
# By Joel Muscat (PuffCode)
# github.com/Puffball101961/matrixticker
# This software is made available under the GNU General Public License
# For more information, refer to the LICENSE file present in the root
# directory of the repository.

import time
import sys
import requests
import requests_cache
import yaml
import os
import math

# Uncomment line below to emulate the matrix in a web browser. Make sure
# You comment out the line importing rgbmatrix as well.
from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
#from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageFilter

#requests_cache.install_cache('http_cache', expire_after=180)

with open("configv2.yml", 'r') as ymlfile:
    cfg = yaml.safe_load(ymlfile)

# User Configuration

CONFIG_ICON_GAP = cfg['iconGap']
CONFIG_PRICE_GAP = cfg['priceGap']
CONFIG_MODULE_LOOP = cfg['moduleLoop']
CONFIG_SLEEP_START = cfg['sleepStart']
CONFIG_SLEEP_BRIGHTNESS = cfg['sleepBrightness']
CONFIG_SLEEP_END = cfg['sleepEnd']
CONFIG_AWAKE_BRIGHTNESS = cfg['awakeBrightness']
CONFIG_SPEED = cfg['scrollSpeed']
CONFIG_SLEEP_CLOCK = cfg['sleepClock']


CONFIG_CRYPTO_ENABLED = cfg['crypto']['enabled']
CONFIG_CRYPTO_FIAT = cfg['crypto']['fiat']
CONFIG_CRYPTO_CURRENCY_PREFIX = cfg['crypto']['currencyPrefix']
CONFIG_CRYPTO_SYMBOLS = cfg['crypto']['symbols']


# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32 # height of the display
options.cols = 128 # width of the display
options.parallel = 1
options.hardware_mapping = 'adafruit-hat-pwm'  # If you have an Adafruit HAT: 'adafruit-hat'
#options.pixel_mapper_config = "Rotate:180" # Rotate 180 degrees if required.
options.led_rgb_sequence = "RBG" # Change to RGB if your matrix has led colors swapped

matrix = RGBMatrix(options = options)

# Fonts
nameFont = ImageFont.load("fonts/pil/6x10.pil")
priceFont = ImageFont.load("fonts/pil/10x20.pil")
changeFont = ImageFont.load("fonts/pil/6x12.pil")

# STARTUP JOBS

# Splash Screen
splash = Image.new('RGBA', (128,32))
draw = ImageDraw.Draw(splash)
draw.text((1,0), "RGB Matrix Ticker", font=nameFont, fill=(255,255,255))
draw.text((1,10), "by PuffCode", font=nameFont, fill=(255,255,255))
draw.text((1,20), "v0.2.4", font=changeFont, fill=(255,255,255))
matrix.SetImage(splash.convert('RGB'))
time.sleep(2)
matrix.Clear()

# Test Network Connection
test = Image.new('RGBA', (128,32))
draw = ImageDraw.Draw(test)
draw.text((1,10), "Connecting...", font=nameFont, fill=(255,255,255))

matrix.SetImage(test.convert('RGB'))

connected = False

# Test Internet Connectivity
while not connected:
    try:
        res = requests.get("https://google.com")
        if res.status_code == 200:
            connected = True
        else:
            matrix.Clear()
            test = Image.new('RGBA', (128,32))
            draw = ImageDraw.Draw(test)
            draw.text((1,10), "Connecting...", font=nameFont, fill=(255,255,255))
            draw.line((2,20,10,28), fill=(255,0,0), width=2)
            draw.line((10,21,2,29), fill=(255,0,0), width=2)
            draw.text((16,20), "Failed, retrying...", font=ImageFont.load('fonts/pil/5x8.pil'), fill=(255,255,255))
            matrix.SetImage(test.convert('RGB'))          
    except:
        matrix.Clear()
        test = Image.new('RGBA', (128,32))
        draw = ImageDraw.Draw(test)
        draw.text((1,10), "Connecting...", font=nameFont, fill=(255,255,255))
        draw.line((2,20,10,28), fill=(255,0,0), width=2)
        draw.line((10,21,2,29), fill=(255,0,0), width=2)
        draw.text((16,20), "Failed, retrying...", font=ImageFont.load('fonts/pil/5x8.pil'), fill=(255,255,255))
        matrix.SetImage(test.convert('RGB'))     
    time.sleep(5)

matrix.Clear()
test = Image.new('RGBA', (128,32))
draw = ImageDraw.Draw(test)
draw.text((1,10), "Connecting...", font=nameFont, fill=(255,255,255))
draw.line((2,22,6,26), fill=(0,255,0), width=2)
draw.line((12,20,6,26), fill=(0,255,0), width=2)
draw.text((16,20), "Connected", font=ImageFont.load('fonts/pil/5x8.pil'), fill=(255,255,255))
draw.text((1,10), "Connecting...", font=nameFont, fill=(255,255,255))
matrix.SetImage(test.convert('RGB'))

time.sleep(2)

# MODULES

# Crypto Module
def cryptoModule():
    # API Calls
    
    res = requests.get("https://api.coingecko.com/api/v3/coins/list")
    if res.status_code == 200:
        coinList = res.json()
    else:
        return {"error": "Non 200 Response Code"}

    cryptoToFetch = CONFIG_CRYPTO_SYMBOLS

    res = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(cryptoToFetch)}&vs_currencies={CONFIG_CRYPTO_FIAT}&include_24hr_change=true&precision=18")
    if res.status_code == 200:
        prices = res.json()
    else:
        return {"error": "Non 200 Response Code"}
    
    # Check if cryptoToFetch ids exist in coinList, and get put the symbol and name into a new dict
    idSymbolDict = {}
    for coin in coinList:
        if coin['id'] in cryptoToFetch:
            idSymbolDict[coin['id']] = coin['symbol']
    
    images = []

    for coin in idSymbolDict:
        image = Image.new('RGBA', (1000,32))
        draw = ImageDraw.Draw(image)
        
        # Check that the icon exists
        if os.path.isfile(f"icons/crypto/{coin}.png"):
            icon = Image.open(f"icons/crypto/{coin}.png")
            image.paste(icon, (0,0))
        else:
            icon = Image.new('RGBA', (0,0))
        
        price = prices[coin][CONFIG_CRYPTO_FIAT]
        symbol = idSymbolDict[coin]
        priceChange = round(prices[coin][f'{CONFIG_CRYPTO_FIAT}_24h_change'], 2)

        if type(price) == float:
            if price < 1:
                price = round(price, 6)
            elif price < 10:
                price = round(price, 4)
            elif price < 1000:
                price = round(price, 2)
            else:
                price = round(price, 0)
                
        price = str(price)
        if len(price.split('.')[1]) < 2:
            price += "0"
        
        if price[-3:] == ".00":
            price = price[:-3]
        
        draw.text((icon.width + CONFIG_ICON_GAP ,-1), f"{symbol.upper()}", font=nameFont, fill=(255,255,255))
        draw.text((icon.width + CONFIG_ICON_GAP ,6), CONFIG_CRYPTO_CURRENCY_PREFIX + str(price), font=priceFont, fill=(255,255,255))
        
        if priceChange > 0:
            draw.text((icon.width + CONFIG_ICON_GAP,22), "%" + str(priceChange), font=changeFont, fill=(0,255,0))

            dist = draw.textlength(str(priceChange), changeFont)
            dist += 7

            draw.polygon([(icon.width + CONFIG_ICON_GAP + dist, 31), (icon.width + CONFIG_ICON_GAP + dist + 3, 26), (icon.width + CONFIG_ICON_GAP + dist + 6, 31)], fill=(0,255,0))

        elif priceChange < 0:
            draw.text((icon.width + CONFIG_ICON_GAP,22), "%" + str(priceChange)[1:], font=changeFont, fill=(255,0,0))

            dist = draw.textlength(str(priceChange)[1:], changeFont)
            dist += 7

            draw.polygon([(icon.width + CONFIG_ICON_GAP + dist, 26), (icon.width + CONFIG_ICON_GAP + dist + 3, 31), (icon.width + CONFIG_ICON_GAP + dist + 6, 26)], fill=(255,0,0))

        elif priceChange == 0:
            priceChange = 0
            draw.text((icon.width + CONFIG_ICON_GAP,22), "%" + str(priceChange), font=changeFont, fill=(0,0,255))

            dist = draw.textlength(str(priceChange), changeFont)
            dist += 8

            draw.ellipse((icon.width + CONFIG_ICON_GAP + dist, 27, icon.width + CONFIG_ICON_GAP + dist + 6, 30), fill=(0,0,255))
        else:
            print("Error: Invalid price change value")
            sys.exit(1)
            
        # Crop image to content
        imgBox = image.getbbox() 
        image = image.crop(imgBox)
        
        images.append(image)    
    return images
    
def renderFrames(renderQueue):
    # Join render queue together
    preImage = Image.new('RGBA', (10,32))
    
    for image in renderQueue:
        tmp = Image.new('RGBA', (preImage.width + image.width + CONFIG_PRICE_GAP, 32))
        tmp.paste(preImage, (0,0))
        tmp.paste(image, (preImage.width,0))
        preImage = tmp
    
    if CONFIG_SPEED == 'slow':
        scroll = 1
    elif CONFIG_SPEED == 'normal':
        scroll = 2
    elif CONFIG_SPEED == 'fast':
        scroll = 3
    else:
        scroll = 2 # Set to normal if config invalid/ missing

    # Render to matrix
    for i in range(0, math.ceil(preImage.width/scroll)):
        tmp = Image.new('RGBA', (128,32))

        preImage = preImage.crop((scroll,0,preImage.width,32))
        tmp.paste(preImage, (0,0))

        matrix.SetImage(tmp.convert('RGB'))

        time.sleep(0.02)
    
renderQueue = []

while True:    
    # Check if the display should be awake or sleeping
    if time.localtime().tm_hour >= CONFIG_SLEEP_END and time.localtime().tm_hour < CONFIG_SLEEP_START:
        matrix.brightness = CONFIG_AWAKE_BRIGHTNESS
        sleeping = False
    else:
        matrix.brightness = CONFIG_SLEEP_BRIGHTNESS
        sleeping = True

    if matrix.brightness != 0: # Don't display anything if the brightness is 0
        if CONFIG_SLEEP_CLOCK and sleeping:
            image = Image.new('RGBA', (128,32))
            draw = ImageDraw.Draw(image)
            
            draw.text((1,0), time.strftime("%I:%M %p"), font=priceFont, fill=(255,255,255))
            draw.text((1,20), time.strftime("%a %d/%m/%Y"), font=nameFont, fill=(255,255,255))
            
            matrix.Clear()
            matrix.SetImage(image.convert('RGB'))
            
            time.sleep(60-time.localtime().tm_sec)
        else:
            if CONFIG_CRYPTO_ENABLED:
                image = cryptoModule()
                if type(image) != dict:
                    renderQueue = []
                    for img in image:
                        renderQueue.append(img)
                
                
            # Copy the render queue to the end of itself, so that the queue is rendered CONFIG_MODULE_LOOP times
            renderQueue = renderQueue * CONFIG_MODULE_LOOP
                
            renderQueue.insert(0, Image.new('RGBA', (128,32)))

            renderFrames(renderQueue)
    else:
        time.sleep(30)
    