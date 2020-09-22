# notify-instock
Looks through products on a webpage and opens a browser when searched product becomes available.

# How to Setup
- Download python 3.8: https://www.python.org/downloads/
- Note: Provided chromedriver downloaded from here: https://chromedriver.storage.googleapis.com/index.html?path=85.0.4183.87/
- Download or Clone this repo
- Download latest chrome (Version 85)
- Open terminal to extracted or cloned repo
- Verify which python 3.8 is in path (Execute proceeding terminal pip cmd)
- python3 -m pip install -r ./requirements.txt
- if failures, add python 3.8 to path and retry

# How to Commands (using python)
- python3 ./src/escraper.py -ne -s "rtx 3080" -aq "&N=100007709&isdeptsrh=1"
- Searches NewEgg for rtx 3080, with desktop graphics card filter query parameter

# Parameter Description
- python3 ./src/escraper.py --help

# Information
This doesn't automate purchase flow. It monitors newegg and checks to see when the first product becomes available. Once it is determined available, the default web browser will open the url to the product. Depending on demand and time, the automation can be implemented on other sites.

We're in this together. Feel free to contribute!

# Features
- Monitors NewEgg listings every 60 seconds
- Opens browser to first available product
- Stops when a product is determined available
- Brings up browser with captcha to manually solve if detected (you may need to restart script after solve)
