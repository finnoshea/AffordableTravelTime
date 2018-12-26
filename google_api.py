#!/usr/bin/env python
"""Provides access to the Google API for finding travel times from a given
address to the SLAC front gate.
"""

__license__ = "GPL"
__version__ = "0.0"
__status__ = "Development"

import os  # to allow directory changes, etc
import csv  # to allow loading the CSV file
import time  # to allow sleeps while geocoding
from collections import defaultdict  # easier dictionary to work with
import googlemaps  # the google maps API
import pandas as pd  # to allow loading of a dataframe
import json  # to allow loading the API
import shared_res # things common to all project parts

class ATTGoogleAPI:
    """
    Class for simplified access to the Google API.
    Class assumes you depart at 8:30 AM and depart at 5:30 PM on January 8, 2019.
    Google API requires a time given as an integer number of seconds from
    January 1, 1970 UTC.

    Methods:

    """
    def __init__(self,morning_time=1546965000,evening_time=1546997400,dataframe=None):
        self.morning_time = morning_time        # depart for work at this time (8:00 AM)
        self.evening_time = evening_time        # depart for home at this time (5:30 PM)
        self.SLAC_address = '2575 Sand Hill Rd, Menlo Park, CA 94025'
        self.SLAC_location = {u'lat': 37.4200135, u'lng': -122.203196} # coords of SLAC gate
        self.dataframe = self.open_dataframe(dataframe)
        self.default_address = '1543 Oriole Ave, Sunnyvale, CA 94087' # default
        self.default_coords = {u'lat': 37.342957, u'lng': -122.0108682} # matches the default
        self.column_names = shared_res.pandas_column_names

        with open("credentials.json", "r") as keyfile: # assumes a local credentials file
            temp_key = json.load(keyfile)
        self.gmaps = googlemaps.Client(key=temp_key["gmap_key"])  # API access to google maps


    def open_dataframe(self,dataframe):
        """opens the dataframe, assumes it is already in memory"""

        if not dataframe: # default is none
            return pd.DataFrame(columns=self.column_names) # make an empty dataframe
        else:
            return pd.DataFrame(datafame)


    def address_to_coords(self,address=None):
        """
        converts a human address into coordinates for directions look-up
        """
        info_dict = self.gmaps.geocode(address=address)
        location = info_dict[0]['geometry']['location']
        place_id = info_dict[0]['place_id']


    def get_directions(self,address=None,mode='driving',departure_time=None):
        """
        get directions from address to SLAC
        modes are one of 'driving', 'walking', 'bicycling' or 'transit'
        """
        info_dict = self.gmaps(origin=address,destination=self.SLAC_address,departure_time=departure_time,mode='driving')
        try:
            info_dict[0] # if the directions failed, this will fail too
        except IndexError:
            duration = 0
            duration_in_traffic = 0
            start_address = u'None'
            start_location = {}
            end_address = u'None'
            end_location = {}
            # fill in the dataframe here
            return # end the function
        # pull out the data for only the first route
        duration = info_dist[0]['legs'][0]['duration']['value'] # integer, number of seconds
        duration_in_traffic = info_dist[0]['legs'][0]['duration_in_traffic']['value'] # integer, number of seconds
        start_address = info_dist[0]['legs'][0]['start_address'] # unicode string
        start_location = info_dist[0]['legs'][0]['start_location'] # location dictionary (coordinates)
        end_address = info_dist[0]['legs'][0]['end_address'] # unicode string
        end_location = info_dist[0]['legs'][0]['end_location'] # location dictionary (coordinates)
        # fill in the dataframe here
