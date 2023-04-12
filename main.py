# RGB Matrix Ticker Software
# By Joel Muscat (PuffCode)

import time
import sys
import asyncio
import aiohttp
import requests
import yaml

from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageFilter

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.safe_load(ymlfile)

# Load config
stocks = cfg['stocks']
cryptoIdBindings = cfg['cryptoIdBindings']
priceCheckThreshold = cfg['priceCheckFrequency']
iconGap = cfg['iconGap']
priceGap = cfg['priceGap']
awakeBrightness = cfg['awakeBrightness']
sleepBrightness = cfg['sleepBrightness']
sleepStart = cfg['sleepStart']
sleepEnd = cfg['sleepEnd']

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 128
options.parallel = 1
options.hardware_mapping = 'adafruit-hat-pwm'  # If you have an Adafruit HAT: 'adafruit-hat'
#options.pixel_mapper_config = "Rotate:180"
options.led_rgb_sequence = "RBG"

matrix = RGBMatrix(options = options)

prevImage = Image.new('RGBA', (128,32))

failConn = False

try:
    testConn = requests.get("https://google.com")
    if testConn.status_code != 200:
        failConn = True
except:
    failConn = True


if failConn == True:
    image = Image.new('RGBA', (128,32))
    draw = ImageDraw.Draw(image)

    icon = Image.open("icons/errors/noApi.png")
    image.paste(icon, (0,12))
    draw.text((0,0), "No Internet Connection", font=ImageFont.load("fonts/pil/5x8.pil"), fill=(255,255,255))
    matrix.SetImage(image.convert('RGB'))

while failConn == True:
    time.sleep(2)
    try:
        testConn = requests.get("https://google.com")
        if testConn.status_code == 200:
            failConn = False
    except:
        pass

def showPrice(assetType, symbol, price, priceChange):
    global prevImage
    nameFont = ImageFont.load("fonts/pil/6x10.pil")
    priceFont = ImageFont.load("fonts/pil/10x20.pil")
    changeFont = ImageFont.load("fonts/pil/6x12.pil")

    image = Image.new('RGBA', (128,32))
    draw = ImageDraw.Draw(image)

    icon = Image.open(f"icons/{assetType}/{symbol}.png")
    image.paste(icon, (0,0))

    while draw.textlength((f"${price}"), priceFont) > 90:
        if type(price) == float:
            #price = round(price, len(str(price).split('.')[1])-1)
            if price < 1:
                price = round(price, 6)
            elif price < 10:
                price = round(price, 4)
            else:
                price = round(price, 2)
        else:
            priceFont = ImageFont.load("fonts/pil/9x18.pil")

    price = str(price)
    
    if len(price.split('.')[1]) < 2:
        price += "0"
    
    if price[-3:] == ".00":
        price = price[:-3]
    

    draw.text((icon.width + iconGap ,-1), f"{symbol.upper()}", font=nameFont, fill=(255,255,255))
    draw.text((icon.width + iconGap ,6), "$" + str(price), font=priceFont, fill=(255,255,255))

    priceChange = round(priceChange, 2)

    if priceChange > 0:
        draw.text((icon.width + iconGap,22), "%" + str(priceChange), font=changeFont, fill=(0,255,0))

        dist = draw.textlength(str(priceChange), changeFont)
        dist += 7

        draw.polygon([(icon.width + iconGap + dist, 31), (icon.width + iconGap + dist + 3, 26), (icon.width + iconGap + dist + 6, 31)], fill=(0,255,0))

    elif priceChange < 0:
        draw.text((icon.width + iconGap,22), "%" + str(priceChange)[1:], font=changeFont, fill=(255,0,0))

        dist = draw.textlength(str(priceChange)[1:], changeFont)
        dist += 7

        draw.polygon([(icon.width + iconGap + dist, 26), (icon.width + iconGap + dist + 3, 31), (icon.width + iconGap + dist + 6, 26)], fill=(255,0,0))

    elif priceChange == 0:
        priceChange = 0
        draw.text((icon.width + iconGap,22), "%" + str(priceChange), font=changeFont, fill=(0,0,255))

        dist = draw.textlength(str(priceChange), changeFont)
        dist += 8

        draw.ellipse((icon.width + iconGap + dist, 27, icon.width + iconGap + dist + 6, 30), fill=(0,0,255))
    else:
        print("Error: Invalid price change value")
        sys.exit(1)


    for i in range(0, 128):
        tmp = Image.new('RGBA', (128,32))

        prevImage = prevImage.crop((1,0,128,32))
        tmp.paste(prevImage, (0,0))

        tmp2 = image.crop((0,0,0+i,32))
        tmp.paste(tmp2, (127-i,0))


        matrix.SetImage(tmp.convert('RGB'))
        time.sleep(0.025)

    time.sleep(displayTime)
    
    prevImage = image

prices = {}
priceCheckIncrement = priceCheckThreshold

async def fetchPrices(cryptoToFetch):
    global prices
    async with aiohttp.ClientSession() as session:
        if len(cryptoToFetch) > 0:
            async with session.get(f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(cryptoToFetch)}&vs_currencies=aud&include_24hr_change=true&precision=18") as resp:
                prices = await resp.json()
        if len(stocks) > 0:
            async with session.get(f"https://query1.finance.yahoo.com/v7/finance/quote?lang=en-US&region=US&corsDomain=finance.yahoo.com&symbols={','.join(stocks)}") as resp:
                sp = await resp.json()
                sp = sp['quoteResponse']['result']
                for stock in sp:
                    prices[stock['symbol']] = {'usd':stock['regularMarketPrice'],'market_change':stock['regularMarketChangePercent']}
    return prices

while True:
    if priceCheckIncrement >= priceCheckThreshold:
        cryptoToFetch = []
        for item in cryptoIdBindings:
            cryptoToFetch.append(cryptoIdBindings[item])

        prices = asyncio.run(fetchPrices(cryptoToFetch))        
        
        priceCheckIncrement = 0
    priceCheckIncrement += 1

    for item in cryptoIdBindings:
        if prices != {}:
            showPrice('crypto', item, prices[cryptoIdBindings[item]]['aud'], prices[cryptoIdBindings[item]]['aud_24h_change'])
        else:
            time.sleep(2)
    for item in stocks:
        if prices != {}:
            showPrice('stock', item, prices[item.upper()]['usd'], prices[item.upper()]['market_change'])
        else:
            time.sleep(2)
    for item in commoditiesIdBindings:
        if prices != {}:
            showPrice('commodity', item, prices[commoditiesIdBindings[item]]['usd'], prices[commoditiesIdBindings[item]]['market_change'])
        else:
            time.sleep(2)

        
