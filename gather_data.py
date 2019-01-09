#!/usr/bin/env python
"""Data collection methods and data storage.
"""

# Because this file uses Firefox via selenium you may need to install
# geckodriver.  If you have homebrew install 'brew install geckodriver' will
# sort it out for you.  You can also download it from the github repo.  It
# needs to be added to your path:
# 'export PATH=$PATH:/path/to/geckodriver/'
# See here for more details:
# https://stackoverflow.com/questions/40208051/selenium-using-python-geckodriver-executable-needs-to-be-in-path


__license__ = "GPL"
__version__ = "0.0"
__status__ = "Development"

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


# Build the class that handles the website actions like searching for
# zipcodes and changing pages.
class zillow_zipcode_search:
    def __init__(self):
        # Load the firefox web driver.
        self.driver         = webdriver.Firefox()

    # Move to the next page in the search.
    def next_page(self):
        self.page_number    = self.page_number + 1
        self.page_to_load   = self.first_page + str(self.page_number) + '_p/'

    # Get the source for the current page to pass to BeautifulSoup
    # Transfer the page source into BeautifulSoup.
    def get_current_page(self):
        self.driver.get(self.page_to_load)
        self.current_page = self.driver.page_source  # extract the source for
        # BeautifulSoup
        return (self.current_page)

    # For testing purposed load some saved pages.
    def get_saved_page(self):
        saved_location =  os.getcwd() +  \
                                         "/saved_pages_for_testing/"
        saved_filename = '94804_OLD.html'
        self.driver.get('file://' + saved_location + saved_filename)
        self.current_page = self.driver.page_source  # extract the source for
        # BeautifulSoup
        return (self.current_page)

    # Run tests on the current page, you're looking for whether the page is a
    #  captcha page or whether there are results on the current page and a
    # few other things.
    def test_current_page(self):
        soup = BeautifulSoup(self.current_page)

        # Test to see if there is a next page.  If there isn't make sure the
        # navigator knows that.  If there is no next page then the result
        # will be an empty list.
        no_next_page = soup.findAll("li", {"class": "zsg-pagination-next"})
        if not no_next_page:
            self.do_next_page = 0

        # # Test to see if zillow says the zipcode is deprected.  If so,
        # # stop searching.
        # deprecated_zip = soup.findAll("div", {"class":"deprecated-zipcode"})
        # if deprecated_zip:
        #     self.no_results = 1
        #     print('Zillow says this zip code is deprecated.')

        # Test to see if there are any results on this page.  If not,
        # tell the iterate to stop trying to change pages.  With the update
        # above which checks for a next button this test is rarely true,
        # but it does rarely come up, so I've left it here.
        no_results = soup.findAll("h3", {"class": "zsg-content_collapsed"})
        try:
            if no_results[0].text == 'No matching results...':
                print("Probably the last page...")
                self.no_results = 1
        except IndexError:
            1+1 # Don't do anything, keep going.  Better to print something?

    # Dump the current master dataframe once the zipcode search is complete.
    def dump_zipcode_dataframe(self, dataframe_in):
        dump_location = os.getcwd() +  "/dumped_data/"
        dump_filename = self.current_zip + ".csv"
        dump_path = dump_location + dump_filename

        # When pandas writes to CSV it converts the datatypes.  This
        # means that the newly created dataframe and the one read from
        # the previously have different dtypes.  This means pandas thinks
        #  they are different and creates new columns with the same name
        # but different dtypes.  Or something.  To get around this you
        # can define the dtype when the dataframe is created or just save
        #  the present dataframe and reload it.  For now, do the latter.
        dataframe_in.to_csv('temp.csv', index=False)
        self.df_new = pd.read_csv('temp.csv')

        # Load the old data and check the current list against the saved list
        #  and only add new listings.  This might be slow.
        try:
            self.df_old = pd.read_csv(dump_path)

            result = pd.concat([self.df_old, self.df_new],
                                            sort='True')
            result = result.drop_duplicates(subset='zillow_id', keep='last')

        except IOError:
            result = self.df_new

        result.to_csv(dump_path, index=False)
        # Remove the temp file.
        os.remove('temp.csv')

    def close_browser(self):
        self.driver.close()

    # This is for testing the inner functioning of the class.  Don't use it
    # in production.
    def testing_function(self):
        print(instance_zillow_scrape.zillow_data_master.filter(regex="zillow_"))

    # Define a search function that updates the page to load.
    def search_zipcode(self, zipcode_in):
        # Reset the flags for doing back to back zipcode searches
        self.do_next_page   = 1
        self.no_results     = 0

        print('Currently scraping zip code: ' + zipcode_in)
        self.page_number = 1
        self.current_zip = zipcode_in
        self.first_page = "https://www.zillow.com/homes/" + zipcode_in + "_rb/"
        self.page_to_load = self.first_page

        # Create an instance of the scraper
        self.instance_zillow_scrape = zillow_parser()

        # Zillow wont return more than 20 pages so use a for loop that
        # automatically stops at 30.  If you make a mistake and it doesn't stop
        #  earlier it won't get stuck in a while.
        for i in range(30):
            # Test the current page to catch last pages and captchas
            self.get_current_page()
            self.test_current_page()
            if self.no_results == 1:
                break
            # Scrape the current page
            self.instance_zillow_scrape.get_houses(self.current_page)
            # Pause to avoid captchas
            time.sleep(np.random.uniform(2, 10))
            # Goto the next page
            if self.do_next_page == 1:
                self.next_page()
            else:
                break

        # Dump the scraped data
        self.dump_zipcode_dataframe(
            self.instance_zillow_scrape.zillow_data_master)

        # Close the web driver
        # self.close_browser()

# Build the class to collect the data from each entry on Zillow.  This class
# takes in html from a web page and extracts the information on all the houses
# displayed on it.
class zillow_parser:
    def __init__(self):
        # Build the master dataframe
        self.zillow_data_master = pd.DataFrame(
            columns=shared_res.pandas_column_names)


    # This function extracts all the houses list on the current page,
    # which is html as extracted from the selenium instance of the web
    # browser.  It returns an iterable list of what zillow calls "cards" that
    #  contain all the information you wish to extract like location and
    # price.  When done, the data is appended to the master dataframe.
    #
    # card_entry is one "card" or search result entry.  A search on zillow
    # returns a bunch of cards which and image and data on the housing unit.
    #  They are stored in the member variable photo_cards.

    def get_houses(self, current_page):
        soup = BeautifulSoup(current_page)
        self.photo_cards = soup.findAll("article",
                                   {"class": "zsg-photo-card photo-card "
                                             "zsg-aspect-ratio type-not-favorite"})
        # Build the pandas data frame to hold the extracted data
        self.zillow_data = pd.DataFrame(
            index = range(len(self.photo_cards)),
            columns=shared_res.pandas_column_names)

        self.iterate_over_house_on_page()

    # Grab longitude and latitude
    def get_location(self, card_entry):
        # Grab longitude and latitude
        temp = card_entry.findAll("meta", {"itemprop": "latitude"})
        # print("Latitude : " + temp[0]['content'])
        lat = temp[0]['content']
        temp = card_entry.findAll("meta", {"itemprop": "longitude"})
        # print("Longitude : " + temp[0]['content'])
        longi = temp[0]['content']
        return(lat, longi)

    # Grab the price and the address, which are contained in the card caption
    def get_card_caption(self, card_entry):
        card_caption = card_entry.findAll("div", {"class"
                                                      : "zsg-photo-card-caption"})
        price = card_entry.findAll("span",
                                        {"class": "zsg-photo-card-price"})
        # If the listing doesn't have a price then "price" will be empty.
        # Set up a try to avoid this case.
        try:
            price = price[0].text
            price = price[1:].replace(',', '')  # Get rid of $ and commas
        except IndexError:
            price = 0

        address = card_entry.findAll("span", {"class" :
                                                  "zsg-photo-card-address"})
        address = address[0].text
        return(price, address)

    # Get the number of days the housing unit has been on zillow.
    def get_days_on(self, card_entry):
        temp = card_entry.findAll("ul", {"class" : "zsg-list_inline "
                                          "zsg-photo-card-badge"})
        try:
            days_on = np.int64(temp[0].text.split(' ')[0])
        except ValueError:
            days_on = 0
        return(days_on)

    # Get the address, this has the information nicely divided unlike the
    # card caption
    def get_address(self, card_entry):
        # Grab longitude and latitude
        temp = card_entry.findAll("span", {"itemprop": "streetAddress"})
        addressStreet = temp[0].text
        temp = card_entry.findAll("span", {"itemprop": "addressLocality"})
        addressCity = temp[0].text
        temp = card_entry.findAll("span", {"itemprop": "addressRegion"})
        addressState = temp[0].text
        temp = card_entry.findAll("span", {"itemprop": "postalCode"})
        zipcode = temp[0].text

        return(zipcode, addressStreet, addressCity, addressState)

    # Get the home type, i.e. manufactured, apartment, whatever.
    # All of the data you captured above is listed here, so you maybe be able
    #  to redo this whole class with one function call.
    def get_home_type(self, card_entry):
        homeType = "0"
        temp = card_entry.findAll("div", {"class": "minibubble template hide"})
        # Convert the output to a string that can be split.
        temp = str(temp[0]).split(',')
        # The location of the hometype entry changes sometimes, so you have
        # to go through the split list.  Yikes.
        for j in temp:
            if (j[1:9] == "homeType"):
                homeType = j.split(':')[1]
                homeType = homeType.strip(' ').strip('"')

        return(homeType)

    # This iterates over the card captions and extracts the listing data.
    def iterate_over_house_on_page(self):
        m = 0
        for k in self.photo_cards:
            # Extract the longitude and latitude
            lat, longi = self.get_location(k)
            price, address = self.get_card_caption(k)
            zipcode, addressStreet, addressCity, addressState = \
                self.get_address(k)
            homeType = self.get_home_type(k)
            days_on = self.get_days_on(k)

            # Drop the information into the dataframe.  I want to keep all
            # the pushing of data into the dataframe in one location to make
            # updates easier.
            self.zillow_data['zillow_id'][m] = k.get('data-zpid')
            self.zillow_data['zillow_status'][m] = k.get('data-pgapt')
            self.zillow_data['zillow_latitude'][m] = lat
            self.zillow_data['zillow_longitude'][m] = longi
            self.zillow_data['zillow_price'][m] = price
            self.zillow_data['zillow_addressStreet'][m] = address
            self.zillow_data['zillow_zipcode'][m] = zipcode
            self.zillow_data['zillow_addressStreet'][m] = addressStreet
            self.zillow_data['zillow_addressCity'][m] = addressCity
            self.zillow_data['zillow_addressState'][m] = addressState
            self.zillow_data['zillow_homeType'][m] = homeType
            self.zillow_data['zillow_days_on'][m] = days_on
            self.zillow_data['date_scraped'][m] = datetime.datetime.now().isoformat()
            # Update the iterator
            m = m + 1

        # Write the data to the master dataframe.
        self.zillow_data_master = self.zillow_data_master.append(
                self.zillow_data, ignore_index=True)

# SBuild the instances needed to perform a zipcode search
some_zillow_zipcode_search = zillow_zipcode_search()

# Run a search for a zipcode
some_zillow_zipcode_search.search_zipcode('94804')

# for H in shared_res.contra_costa_county_zip:
#     some_zillow_zipcode_search.search_zipcode(H)


