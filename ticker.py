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

from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageFilter

requests_cache.install_cache('http_cache', expire_after=180)

with open("configv2.yml", 'r') as ymlfile:
    cfg = yaml.safe_load(ymlfile)


CONFIG_ICON_GAP = cfg['iconGap']
CONFIG_PRICE_GAP = cfg['priceGap']
CONFIG_MODULE_LOOP = cfg['moduleLoop']
CONFIG_SLEEP_START = cfg['sleepStart']
CONFIG_SLEEP_BRIGHTNESS = cfg['sleepBrightness']
CONFIG_SLEEP_END = cfg['sleepEnd']
CONFIG_AWAKE_BRIGHTNESS = cfg['awakeBrightness']
CONFIG_DISPLAY_MODE = cfg['displayMode']
CONFIG_TOP_MODULES = cfg['topDisplayModules']
CONFIG_BOTTOM_MODULES = cfg['bottomDisplayModules']


CONFIG_CRYPTO_ENABLED = cfg['crypto']['enabled']
CONFIG_CRYPTO_SYMBOLS = cfg['crypto']['symbols']


# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 128
options.parallel = 1
options.hardware_mapping = 'adafruit-hat-pwm'  # If you have an Adafruit HAT: 'adafruit-hat'
#options.pixel_mapper_config = "Rotate:180"
options.led_rgb_sequence = "RBG"

matrix = RGBMatrix(options = options)

# Fonts
nameFont = ImageFont.load("fonts/pil/6x10.pil")
priceFont = ImageFont.load("fonts/pil/10x20.pil")
changeFont = ImageFont.load("fonts/pil/6x12.pil")



# STARTUP JOBS

# # Splash Screen
# splash = Image.new('RGBA', (128,32))
# draw = ImageDraw.Draw(splash)
# draw.text((1,0), "RGB Matrix Ticker", font=nameFont, fill=(255,255,255))
# draw.text((1,10), "by PuffCode", font=nameFont, fill=(255,255,255))
# draw.text((1,20), "v0.1", font=changeFont, fill=(255,255,255))
# matrix.SetImage(splash.convert('RGB'))
# time.sleep(2)
# matrix.Clear()

# Test Network Connection
test = Image.new('RGBA', (128,32))
draw = ImageDraw.Draw(test)
draw.text((1,10), "Connecting...", font=nameFont, fill=(255,255,255))

matrix.SetImage(test.convert('RGB'))

connected = False

while not connected:
    print('test')
    try:
        res = requests.get("https://google.com")
        if res.status_code == 200:
            connected = True
        else:
            draw.line((2,20,10,28), fill=(255,0,0), width=2)
            draw.line((10,21,2,29), fill=(255,0,0), width=2)
            draw.text((16,20), "Failed, retrying...", font=ImageFont.load('fonts/pil/5x8.pil'), fill=(255,255,255))
            matrix.SetImage(test.convert('RGB'))          
    except:
        draw.line((2,20,10,28), fill=(255,0,0), width=2)
        draw.line((10,21,2,29), fill=(255,0,0), width=2)
        draw.text((16,20), "Failed, retrying...", font=ImageFont.load('fonts/pil/5x8.pil'), fill=(255,255,255))
        matrix.SetImage(test.convert('RGB'))     
    time.sleep(5)

matrix.Clear()

draw.line((2,22,6,26), fill=(0,255,0), width=2)
draw.line((12,20,6,26), fill=(0,255,0), width=2)
draw.text((16,20), "Connected", font=ImageFont.load('fonts/pil/5x8.pil'), fill=(255,255,255))
draw.text((1,10), "Connecting...", font=nameFont, fill=(255,255,255))
matrix.SetImage(test.convert('RGB'))

time.sleep(1000)

# MODULES

# Crypto Module
def cryptoModule(mode: str = 'full'):
    # API Calls
    
    res = requests.get("https://api.coingecko.com/api/v3/coins/list")
    if res.status_code == 200:
        coinList = res.json()
    else:
        return {"error": "Non 200 Response Code"}

    cryptoToFetch = CONFIG_CRYPTO_SYMBOLS

    res = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(cryptoToFetch)}&vs_currencies=aud&include_24hr_change=true&precision=18")
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
        
        icon = Image.open(f"icons/crypto/{coin}.png")
        image.paste(icon, (0,0))
        
        price = prices[coin]['aud']
        symbol = idSymbolDict[coin]
        priceChange = round(prices[coin]['aud_24h_change'], 2)

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
        draw.text((icon.width + CONFIG_ICON_GAP ,6), "$" + str(price), font=priceFont, fill=(255,255,255))
        
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
            
        if draw.textlength(f"{symbol.upper()} ${price}", nameFont) < draw.textlength(f"%{priceChange}", changeFont) + 7:
            image = image.crop((0,0,icon.width + CONFIG_ICON_GAP + draw.textlength(f"%{priceChange}", changeFont)+7,32))
        else:
            image = image.crop((0,0,icon.width + CONFIG_ICON_GAP + draw.textlength(f"${price}", priceFont),32))
        
        images.append(image)
    
    return images
    

def renderFrames(renderQueue, mode: str = "full"):
    # Join render queue together
    preImage = Image.new('RGBA', (10,32))
    
    for image in renderQueue:
        tmp = Image.new('RGBA', (preImage.width + image.width + CONFIG_PRICE_GAP, 32))
        tmp.paste(preImage, (0,0))
        tmp.paste(image, (preImage.width,0))
        preImage = tmp
    
    # Render to matrix
    for i in range(0, preImage.width):
        tmp = Image.new('RGBA', (128,32))

        preImage = preImage.crop((1,0,preImage.width,32))
        tmp.paste(preImage, (0,0))

        matrix.SetImage(tmp.convert('RGB'))

        time.sleep(0.025)
    

while True:    
    # Check if the display should be awake or sleeping
    if time.localtime().tm_hour >= CONFIG_SLEEP_END and time.localtime().tm_hour < CONFIG_SLEEP_START:
        matrix.brightness = CONFIG_AWAKE_BRIGHTNESS
    else:
        matrix.brightness = CONFIG_SLEEP_BRIGHTNESS
        
    if CONFIG_DISPLAY_MODE == "full":
        renderQueue = []
        if CONFIG_CRYPTO_ENABLED:
            image = cryptoModule()
            if type(image) == dict:
                print(image['error'])
                sys.exit(1)
            else:
                renderQueue.append(image)
                
                
        # Copy the render queue to the end of itself, so that the queue is rendered CONFIG_MODULE_LOOP times
        renderQueue = renderQueue * CONFIG_MODULE_LOOP
            
        renderQueue.insert(0, Image.new('RGBA', (128,32)))

        renderFrames(renderQueue, CONFIG_DISPLAY_MODE)
    
    
    elif CONFIG_DISPLAY_MODE == "half":
        renderQueueTop = []
        renderQueueBottom = []
        if CONFIG_CRYPTO_ENABLED:
            image = cryptoModule('half')
            if type(image) == dict:
                print(image['error'])
                sys.exit(1)
            else:
                if 'crypto' in CONFIG_TOP_MODULES:
                    renderQueueTop.append(image)
                elif 'crypto' in CONFIG_BOTTOM_MODULES:
                    renderQueueBottom.append(image)
                else:
                    renderQueueTop.append(image)
                
        # Copy the render queue to the end of itself, so that the queue is rendered CONFIG_MODULE_LOOP times
        renderQueueTop = renderQueueTop * CONFIG_MODULE_LOOP
        renderQueueBottom = renderQueueBottom * CONFIG_MODULE_LOOP
        
        renderQueueTop.insert(0, Image.new('RGBA', (128,32)))
        renderQueueBottom.insert(0, Image.new('RGBA', (128,32)))

        
        renderFrames([renderQueueTop, renderQueueBottom], CONFIG_DISPLAY_MODE)