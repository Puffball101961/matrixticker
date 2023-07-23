# RGB Matrix Ticker Software Tezos Edition
# By Joel Muscat (PuffCode)
# github.com/Puffball101961/matrixticker

import time
import sys
import asyncio
import aiohttp
import requests
import yaml
from datetime import datetime

from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageFilter

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.safe_load(ymlfile)

# Load config
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

# Get Tezos Price in AUD, and 24h change in %
def getTezosPrice():
    request = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=tezos&vs_currencies=aud&include_24hr_change=true")
    requestJSON = request.json()
    tezosPrice = requestJSON['tezos']['aud']
    tezosPrice = str(round(tezosPrice, 2))
    
    # If the price is divisible by 0.1, add a 0 to the end, using the length after the decimal
    if len(tezosPrice.split('.')[1]) == 1:
        tezosPrice = tezosPrice + "0"

    tezosChange = requestJSON['tezos']['aud_24h_change']
    tezosChange = str(round(tezosChange, 2))

    return tezosPrice, tezosChange

# Get the current proposal alias, current period, total votes and time remaining.
def getVoting():
    request = requests.get("https://api.tzkt.io/v1/voting/epochs/latest_voting")
    requestJSON = request.json()
    allProposals = requestJSON['proposals']
    for proposal in allProposals:
        if proposal['status'] == 'active':
            currentProposal = proposal['extras']['alias']
    
    currentPeriod = requestJSON['periods'][-1]
    periodName = currentPeriod['kind']
    periodStatus = currentPeriod['status']
    periodEnd = currentPeriod['endTime']
    supermajority = currentPeriod['supermajority']
    quorum = currentPeriod['ballotsQuorum']
    totalVP = currentPeriod['totalVotingPower']
    yayVP = currentPeriod['yayVotingPower']
    nayVP = currentPeriod['nayVotingPower']
    passVP = currentPeriod['passVotingPower']

    # Return as dict
    return {
        'currentProposal': currentProposal,
        'periodName': periodName,
        'periodStatus': periodStatus,
        'periodEnd': periodEnd,
        'supermajority': supermajority,
        'quorum': quorum,
        'totalVP': totalVP,
        'yayVP': yayVP,
        'nayVP': nayVP,
        'passVP': passVP
    }

# Get current block and cycle
def getBlockchainInfo():
    request = requests.get("https://api.tzkt.io/v1/head")
    requestJSON = request.json()
    currentBlock = requestJSON['level']
    currentCycle = requestJSON['cycle']
    return currentBlock, currentCycle


# Main Matrix Loop
while True:
    # Check if the display should be awake or sleeping
    if time.localtime().tm_hour >= sleepEnd and time.localtime().tm_hour < sleepStart:
        matrix.brightness = awakeBrightness
    else:
        # matrix.brightness = sleepBrightness
        matrix.brightness = awakeBrightness # DEBUG ONLY

    # # Get Tezos Price every 5 minutes
    # if time.localtime().tm_min % 5 == 0:
    #     tezosPrice, tezosChange = getTezosPrice()
    
    # # Get Voting Info Every 30 minutes
    # if time.localtime().tm_min % 30 == 0:
    #     votingInfo = getVoting()

    # # Get Blockchain Info Every 30 seconds
    # if time.localtime().tm_sec % 30 == 0:
    #     currentBlock, currentCycle = getBlockchainInfo()
    
    # TEMP VALUES
    tezosPrice = "1.43"
    tezosChange = "-1.0"
    votingInfo = {
        'currentProposal': "Nairobi",
        'periodName': "Promotion",
        'periodStatus': "active",
        'periodEnd': "2023-06-28T12:00:00Z",
        'supermajority': 80,
        'quorum': 20.5,
        'totalVP': 530000000,
        'yayVP': 50000000,
        'nayVP': 20000000,
        'passVP': 30000000
    }
    currentBlock = 123456
    currentCycle = 1234

    image = Image.new('RGBA', (128,32))
    draw = ImageDraw.Draw(image)

    # Draw Tezos Price
    draw.text((0,0), "$" + tezosPrice, font=ImageFont.load("fonts/pil/6x9.pil"), fill=(255,255,255))
    priceLength = draw.textlength("$" + tezosPrice, font=ImageFont.load("fonts/pil/6x9.pil"))
    if float(tezosChange) > 0:
        draw.polygon([(priceLength + 1, 4), (priceLength + 3, 2), (priceLength + 5, 4)], fill=(0,255,0))
        draw.text((priceLength + 7,0), tezosChange + "%", font=ImageFont.load("fonts/pil/6x9.pil"), fill=(0,255,0))
    
    elif float(tezosChange) < 0:
        draw.polygon([(priceLength + 1, 2), (priceLength + 3, 4), (priceLength + 5, 2)], fill=(255,0,0))
        draw.text((priceLength + 7,0), tezosChange[1:] + "%", font=ImageFont.load("fonts/pil/6x9.pil"), fill=(255,0,0))
    
    # If no change, do a blue circle
    else:
        draw.ellipse([(priceLength + 1, 2), (priceLength + 3, 5)], fill=(0,0,255))
        draw.text((priceLength + 5,0), tezosChange + "%", font=ImageFont.load("fonts/pil/6x9.pil"), fill=(0,0,255))


    # Draw Voting Info
    # draw.text((0, 10), votingInfo['currentProposal'] + " - " + votingInfo['periodName'], font=ImageFont.load("fonts/pil/5x7.pil"), fill=(255,255,255))
    # infoLen = draw.textlength(votingInfo['currentProposal'] + " - " + votingInfo['periodName'], font=ImageFont.load("fonts/pil/5x7.pil"))

    # Display time left in Minutes, Hours and Days, depending on how long is left and the space available. Dont include seconds
    timeLeft = datetime.strptime(votingInfo['periodEnd'], "%Y-%m-%dT%H:%M:%SZ") - datetime.utcnow()

    # If there is more than 7 days left, display in days
    if timeLeft.days >= 7:
        textwidth = draw.textlength(str(timeLeft.days) + "d", font=ImageFont.load("fonts/pil/5x7.pil"))
        draw.text((128-textwidth, 1), str(timeLeft.days) + "d", anchor="ra", font=ImageFont.load("fonts/pil/5x7.pil"), fill=(100,100,255))

    # If there is more than 1 day left, display in days and hours
    elif timeLeft.days > 0:
        textwidth = draw.textlength(str(timeLeft.days) + "d " + str(timeLeft.seconds // 3600) + "h", font=ImageFont.load("fonts/pil/5x7.pil"))
        draw.text((128-textwidth, 1), str(timeLeft.days) + "d " + str(timeLeft.seconds // 3600) + "h", font=ImageFont.load("fonts/pil/5x7.pil"), fill=(100,100,255))

    # If there is more than 1 hour left, display in hours and minutes
    elif timeLeft.seconds // 3600 > 0:
        textwidth = draw.textlength(str(timeLeft.seconds // 3600) + "h " + str((timeLeft.seconds % 3600) // 60) + "m", font=ImageFont.load("fonts/pil/5x7.pil"))
        draw.text((128-textwidth, 1), str(timeLeft.seconds // 3600) + "h " + str((timeLeft.seconds % 3600) // 60) + "m", font=ImageFont.load("fonts/pil/5x7.pil"), fill=(100,100,255))
    
    # If there is more than 1 minute left, display in minutes
    elif timeLeft.seconds // 60 > 0:
        textwidth = draw.textlength(str(timeLeft.seconds // 60) + "m", font=ImageFont.load("fonts/pil/5x7.pil"))
        draw.text((128-textwidth, 1), str(timeLeft.seconds // 60) + "m", font=ImageFont.load("fonts/pil/5x7.pil"), fill=(100,100,255))

    else:
        textwidth = draw.textlength("<1m", font=ImageFont.load("fonts/pil/5x7.pil"))
        draw.text((128-textwidth, 1), "<1m", font=ImageFont.load("fonts/pil/5x7.pil"), fill=(100,100,255))

    # Draw a horizontal segmented bar graph for voted and not voted, and a white line for the quorum, based on the percentage of votes
    votedPercentage = (votingInfo['passVP'] + votingInfo['yayVP'] + votingInfo['nayVP']) / votingInfo['totalVP']

    # Draw green segment for voted
    draw.rectangle([(0, 10), (round(128*votedPercentage,0), 11)], fill=(0,255,0))

    # Draw red segment for not voted
    draw.rectangle([(round(128*votedPercentage,0), 10), (128, 11)], fill=(255,0,0))

    # # Draw white line for quorum
    draw.line([(128 * votingInfo['quorum'] / 100, 10), (128 * votingInfo['quorum'] / 100, 11)], fill=(255,255,255))
    
    # Draw a horizontal segmented bar graph for yay, nay and pass, based on the percentage of votes
    # Draw green segment for yay
    draw.rectangle([(0, 13), (round(128*votingInfo['yayVP']/(votingInfo['yayVP'] + votingInfo['nayVP']),0), 14)], fill=(0,255,0))

    # Draw red segment for nay
    draw.rectangle([(round(128*votingInfo['yayVP']/(votingInfo['yayVP'] + votingInfo['nayVP']),0) ,13),(128,14)], fill=(255,0,0))


    # Draw a white line for the supermajority, based on the percentage of votes
    draw.line([(128 * votingInfo['supermajority'] / 100, 13), (128 * votingInfo['supermajority'] / 100, 14)], fill=(255,255,255))

    # draw.text((0, 17), f"Quorum: {round(votedPercentage*100,1)}%/{votingInfo['quorum']}%", font=ImageFont.load("fonts/pil/5x7.pil"), fill=(255,255,255))
    # draw.text((0, 25), f"Ballot: {round(votedPercentage*100,1)}%/{votingInfo['quorum']}%", font=ImageFont.load("fonts/pil/5x7.pil"), fill=(255,255,255))
    draw.text((0, 17), f"Quorum: ", font=ImageFont.load("fonts/pil/5x7.pil"), fill=(255,255,255))
    length = draw.textlength(f"Quorum: ", font=ImageFont.load("fonts/pil/5x7.pil"))
    if votedPercentage*100 < votingInfo['quorum']:
        draw.text((length, 17), f"{round(votedPercentage*100,1)}%/{votingInfo['quorum']}%", font=ImageFont.load("fonts/pil/5x7.pil"), fill=(255,0,0))
    else:
        draw.text((length, 17), f"{round(votedPercentage*100,1)}%/{votingInfo['quorum']}%", font=ImageFont.load("fonts/pil/5x7.pil"), fill=(0,255,0))

    draw.text((0, 25), f"Ballot: ", font=ImageFont.load("fonts/pil/5x7.pil"), fill=(255,255,255))
    length = draw.textlength(f"Ballot: ", font=ImageFont.load("fonts/pil/5x7.pil"))

    if votedPercentage*100 < votingInfo['supermajority']:
        draw.text((length, 25), f"{round(100*votingInfo['yayVP']/(votingInfo['yayVP'] + votingInfo['nayVP']),1)}%/{votingInfo['supermajority']}%", font=ImageFont.load("fonts/pil/5x7.pil"), fill=(255,0,0))
    else:
        draw.text((length, 25), f"{round(100*votingInfo['yayVP']/(votingInfo['yayVP'] + votingInfo['nayVP']),1)}%/{votingInfo['supermajority']}%", font=ImageFont.load("fonts/pil/5x7.pil"), fill=(0,255,0))


    matrix.SetImage(image.convert('RGB'))