# RGB Matrix Ticker
RGB Matrix Crypto and Stock Ticker based on a Raspberry Pi

I'm not a pro 3d modeller or programmer so pls don't attack me :)
This project was a part of hackclub.com 's Winter Hardware Wonderland Program.

This Project is not 100% complete, and is not foolproof. You will need some knowledge and common sense to get it working.
I am planning to refine the process when I have time to work on it.

## Make your own:
https://www.instructables.com/Cryptocurrency-and-Stock-Price-Ticker/

## Adding more symbols
I am planning on automating this process soon.
To add more crypto/ stock symbols to your ticker you need to do the following:
**Crypto:**
1: Find the crypto you want to add on Coingecko, and locate it's API ID
2: Add a dictionary entry into the cryptoIdBindings dictionary, following the format 'displayName':'coingeckoID'
3: Add an icon with maximum dimensions of 32x32px (doesn't have to be square) into icons/crypto, with the same name as the displayName
**Stock:**
1: Find the stock you want to add on Yahoo Finance
2: Add a string entry into the stocks list
3: Add an icon with maximum dimensions of 32x32px (doesn't have to be square) into icons/stock, with the same name as the stock symbol
**Commodity:**
1: Find the stock you want to add on Yahoo Finance and locate it's API ID
2: Add a dictionary entry into the commoditiesIdBindings dictionary, following the format 'displayName':'yahooFinanceAPI'
Add an icon with maximum dimensions of 32x32px (doesn't have to be square) into icons/commodity, with the same name as the displayName

## Contributing
I will be welcoming improvements and extra features to the code. Open a PR with your proposed changes and I will have a look.

## License
This Open Source software is distributed under the GNU GPLv3 license. It is distributed with no Warranty and I incur no Liability from your use of this software. You may modify this code however you like, and distribute it. Source code must be made available if you are distributing. You are not allowed to create closed source software based on this code. More info can be found at this website: https://choosealicense.com/licenses/gpl-3.0/

