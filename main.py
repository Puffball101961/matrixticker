# RGB Matrix Ticker Software
# By Joel Muscat (PuffCode)

import time
import sys
import asyncio
import aiohttp
import requests

#from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageFilter


stocks = [
    'aapl',
    'amzn',
    'goog',
    'msft'
]

cryptoIdBindings = { # Coingecko API ID bindings
    'btc': 'bitcoin',
    'ltc': 'litecoin',
    'eth': 'ethereum',
    'matic': 'matic-network',
    # 'near': 'near',
    # 'xrp': 'ripple',
    'xtz': 'tezos',
    'sol': 'solana',
}

commoditiesIdBindings = { # Yahoo Finance API ID bindings
    # 'gold': 'GC=F',
    # 'silver': 'SI=F',
    # 'copper': 'HG=F',
    # 'crudeoil': 'CL=F'
}

priceCheckThreshold = 10    # How many times the ticker should cycle through before checking for new prices

iconGap = 6 # How much space should be between the icon and the text

priceGap = 10 # How much space should be between each price ticker

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

def genPrice(assetType, symbol, price, priceChange):
#     global prevImage
    nameFont = ImageFont.load("fonts/pil/6x10.pil")
    priceFont = ImageFont.load("fonts/pil/10x20.pil")
    changeFont = ImageFont.load("fonts/pil/6x12.pil")

    image = Image.new('RGBA', (1000,32))
    draw = ImageDraw.Draw(image)

    icon = Image.open(f"icons/{assetType}/{symbol}.png")
    image.paste(icon, (0,0))

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

    # crop the image horizontally to the width of the content
    # Check if price width is lonnger than price change width
    if draw.textlength(f"{symbol.upper()} ${price}", nameFont) < draw.textlength(f"%{priceChange}", changeFont) + 7:
        image = image.crop((0,0,icon.width + iconGap + draw.textlength(f"%{priceChange}", changeFont)+7,32))
    else:
        image = image.crop((0,0,icon.width + iconGap + draw.textlength(f"${price}", priceFont),32))
    return image

lastImage = None

# Use the genPrice function to create a long image of all the prices in the symbol, price and priceChange lists, then scroll it across the screen.
def showPrice(prices):
    global lastImage
    # Create a new image
    preImage = Image.new('RGBA', (10,32))


    for item in cryptoIdBindings:
        image = genPrice('crypto', item, prices[cryptoIdBindings[item]]['aud'], prices[cryptoIdBindings[item]]['aud_24h_change'])
        # append the image to preImage, after expandng preImage to fit the new image, adding a 10 pixel gap between images

        tmp = Image.new('RGBA', (preImage.width + image.width + priceGap, 32))
        tmp.paste(preImage, (0,0))
        tmp.paste(image, (preImage.width,0))
        preImage = tmp
    
    for item in stocks:
        image = genPrice('stock', item.upper(), prices[item.upper()]['usd'], prices[item.upper()]['market_change'])
        # append the image to preImage, after expandng preImage to fit the new image, adding a 10 pixel gap between images

        tmp = Image.new('RGBA', (preImage.width + image.width + priceGap, 32))
        tmp.paste(preImage, (0,0))
        tmp.paste(image, (preImage.width,0))
        preImage = tmp

    # Paste the last image to the start of preImage, allowing for a smooth transition
    if lastImage != None:
        tmp = Image.new('RGBA', (preImage.width + lastImage.width, 32))
        tmp.paste(lastImage, (0,0))
        tmp.paste(preImage, (lastImage.width-10,0))
        preImage = tmp

    # scroll through preImage
    for i in range(0, preImage.width-128):
        tmp = Image.new('RGBA', (128,32))

        preImage = preImage.crop((1,0,preImage.width,32))
        tmp.paste(preImage, (0,0))

        matrix.SetImage(tmp.convert('RGB'))

        time.sleep(0.01)
    
    lastImage = tmp


prices = {}
priceCheckIncrement = priceCheckThreshold

async def fetchPrices(cryptoToFetch, comsToFetch):
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
        if len(comsToFetch) > 0:
            async with session.get(f"https://query1.finance.yahoo.com/v7/finance/quote?lang=en-US&region=US&corsDomain=finance.yahoo.com&symbols={','.join(comsToFetch)}") as resp:
                cp = await resp.json()
                cp = cp['quoteResponse']['result']
                for com in cp:
                    prices[com['symbol']] = {'usd':com['regularMarketPrice'],'market_change':com['regularMarketChangePercent']}
    return prices

while True:
    if priceCheckIncrement >= priceCheckThreshold:
        cryptoToFetch = []
        for item in cryptoIdBindings:
            cryptoToFetch.append(cryptoIdBindings[item])

        comsToFetch = []
        for item in commoditiesIdBindings:
            comsToFetch.append(commoditiesIdBindings[item])

        prices = asyncio.run(fetchPrices(cryptoToFetch, comsToFetch))        
        
        priceCheckIncrement = 0
    priceCheckIncrement += 1

    if prices != {}:
        showPrice(prices)
    else:
        time.sleep(2)


        
