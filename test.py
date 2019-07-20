
##
# This file is for running quick tests outside of the class structure.

# Set up the imports to run the scrape.
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from BeautifulSoup import BeautifulSoup
import shared_res
import pandas as pd
import numpy as np
import os
import time # gonna wanna pause to avoid captchas
import datetime


page_to_load    = 'https://www.zillow.com/homes/94104_rb/'
driver          = webdriver.Firefox()
driver.get(page_to_load)
current_page    = driver.page_source
# soup            = BeautifulSoup(current_page, features="html5lib")
soup            = BeautifulSoup(current_page)


# deprecated_zip  = soup.findAll("div", {"class":"deprecated-zipcode"})


not_next = soup.findAll("li", {"class": "zsg-pagination-next"})




