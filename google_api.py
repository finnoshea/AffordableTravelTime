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
import numpy as np # use numpy
import json  # to allow loading the API
import shared_res # things common to all project parts

class ATTGoogleAPI:
    """
    Class for simplified access to the Google API.
    Class assumes you depart at 8:30 AM and depart at 5:30 PM on January 8, 2019.
    Google API requires a time given as an integer number of seconds from
    January 1, 1970 UTC.

    Functions:

    """
    def __init__(self,morning_time=1546965000,evening_time=1546997400,dataframe=None):
        self.morning_time = morning_time        # depart for work at this time (8:00 AM)
        self.evening_time = evening_time        # depart for home at this time (5:30 PM)
        self.SLAC_address = '2575 Sand Hill Rd, Menlo Park, CA 94025'
        self.SLAC_location = {u'lat': 37.4200135, u'lng': -122.203196} # coords of SLAC gate
        self.default_address = '1543 Oriole Ave, Sunnyvale, CA 94087' # default
        self.default_location = {u'lat': 37.342957, u'lng': -122.0108682} # matches the default
        self.column_names = shared_res.pandas_column_names
        self.dtypes = shared_res.pandas_dtypes
        self.df = self.open_dataframe(dataframe)

        with open("credentials.json", "r") as keyfile: # assumes a local credentials file
            temp_key = json.load(keyfile)
        self.gmaps = googlemaps.Client(key=temp_key["gmap_key"])  # API access to google maps


    def open_dataframe(self,dataframe=None):
        """opens the dataframe, assumes it is already in memory"""

        if not dataframe: # default is none
            return pd.DataFrame(columns=self.column_names) # make an empty dataframe
        else: # data is saved in CSV files
            return pd.read_csv(dataframe,dtype=self.dtypes)


    def save_dataframe_csv(self,path_to_csv):
        """ saves an open dataframe as a CSV """

        self.df.to_csv(path_to_csv,index=False) # save the file
        self.df = self.open_dataframe(dataframe=None) # replace it in memory


    def address_to_coords(self,address=None):
        """
        converts a human address into coordinates for directions look-up
        """
        info_dict = self.gmaps.geocode(address=address)
        location = info_dict[0]['geometry']['location']
        place_id = info_dict[0]['place_id']


    def convert_coords(self,lat=None,lng=None):
        """
        convert coordinates to a dictionary format accepted by the gmaps API

        expected use is:
        self.dataframe['location'] = self.dataframe.apply(lambda row:
                            self.convert_coords(row['lat'],row['lng']),axis=1)
        """
        if isinstance(lat,str):
            lat = float(lat)
        if isinstance(lng,str):
            lat = float(lng)
        return {u'lat': lat, u'lng': lng}


    def price_filter(self,price_str):
        """fixes formatting issues with prices, makes the strings ints"""
        if price_str[-1] is 'K':
            return int(price_str[:-1] + '000')
        elif price_str[-1] is '+':
            return int(price_str[:-1])
        elif price_str[-1] is 'M':
            return int(float(price_str[:-1]) * 1000000)
        else:
            return int(price_str)


    def get_drive_time(self,location=None,departure_time='morning'):
        """
        get directions from location (GPS coordinates) to SLAC for driving
        departure_time can be 'morning', 'evening' or a time accepted by the API
        """
        if not location: # if the location is None
            location = self.default_location
        if departure_time == 'morning':
            departure_time = self.morning_time
        elif departure_time == 'evening':
            departure_time = self.evening_time

        info_dict = self.gmaps(origin=location,
                               destination=self.SLAC_address,
                               departure_time=departure_time,
                               mode='driving',
                               traffic_model='best_guess')
        try:
            info_dict[0] # if the directions failed, this will fail too
        except IndexError:
            duration = -1
            duration_in_traffic = -1
            start_address = u'None'
            start_location = {}
            end_address = u'None'
            end_location = {}
            return start_address, start_location, end_address, end_location, duration, duration_in_traffic
        # pull out the data for only the first route
        duration = info_dist[0]['legs'][0]['duration']['value'] # integer, number of seconds
        duration_in_traffic = info_dist[0]['legs'][0]['duration_in_traffic']['value'] # integer, number of seconds
        start_address = info_dist[0]['legs'][0]['start_address'] # unicode string
        start_location = info_dist[0]['legs'][0]['start_location'] # location dictionary (coordinates)
        end_address = info_dist[0]['legs'][0]['end_address'] # unicode string
        end_location = info_dist[0]['legs'][0]['end_location'] # location dictionary (coordinates)
        return start_address, start_location, end_address, end_location, duration, duration_in_traffic


    def load_files(self,dump_location=None):
        """
        open each of the zipcode files and create one large dataframe
        """
        if not dump_location: # default (None) is to look in /dumped_data/
            dump_location = os.getcwd() +  "/dumped_data/"
        # iterate through the files in the desired directory
        df = self.open_dataframe(None) # create a blank dataframe

        for file_str in os.listdir(dump_location):
            #print 'Opening {:s}'.format(file_str)
            dump_path = dump_location + file_str
            dtf = self.open_dataframe(dump_path)
            if file_str.split('.')[-1] == 'csv': # only open CSV files
                df = df.append(dtf,ignore_index=True) # append the new dataframe
        self.df = df # update self.dataframe


    def process_data(self):
        """transform the data in useful ways"""
        if len(self.df) < 1:
            print 'No data yet loaded.  Run load_files first.'
            return

        # do some filtering of entries we don't want to see
        filter1 = self.df['zillow_status'].isin(['ForSale','RecentlySold']) # only want sales for now
        # it appears that all recently sold have a price of '0'
        filter2 = ~self.df['zillow_price'].isin(['0']) # all prices that are NOT zero
        self.df = self.df[filter1 & filter2] # keep only the desired data

        # turn the zillow_id into an integer
        self.df['zillow_id'] = self.df['zillow_id'].astype(int)

        # turn the date scraped in to a datetime
        self.df['date_scraped'] = pd.to_datetime(self.df['date_scraped'])

        # zillow_prices is all screwy with various numbering formats, fix this
        self.df['zillow_price'] = self.df['zillow_price'].apply(self.price_filter)

        # for all the coords, make a dictionary for the google API
        self.df['location'] = self.df.apply(lambda row:
                              self.convert_coords(row['zillow_latitude'],
                              row['zillow_longitude']),axis=1)


    def save_dataframe_hdf(self,save_file='saved_data.hdf5'):
        # if the file exists, remove it
        if save_file in os.listdir('./'):
            os.remove(save_file)
        # create the saved file
        hdf_file = pd.HDFStore(save_file)
        hdf_file.put('all_zips',self.df)
        hdf_file.close()


    def process_files(self,dump_location=None,save_file='saved_data.hdf5'):
        """typical use pattern for file processing"""
        self.load_files(dump_location=dump_location)
        self.process_data()
        self.save_dataframe_hdf(save_file=save_file)
