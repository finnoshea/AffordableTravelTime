#!/usr/bin/env python
"""
Provides access to the Google API for finding travel times from a given
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
import datetime # for checking processing success

# if you have pandas 23.4 or newer, you can ignore np.inf as well as np.nan
if float('.'.join(pd.__version__.split('.')[1:])) >= 23.4 :
    pd.options.mode.use_inf_as_na = True

class ATTGoogleAPI:
    """
    Class for simplified access to the Google API.
    Class assumes you depart at 8:00 AM for work and
    depart at 5:30 PM for home both on Feb 26, 2019.
    Google API requires a time given as an integer number of seconds from
    January 1, 1970 UTC.

    If you have Pandas 23.4 or newer, dataframe functions (like .mean()) will
    ignore np.inf as well as np.nan.  np.inf is used to signify a travel time
    that google could not compute some how.  Using the newer Pandas greatly
    simplifies column computations on the durations columns.

    For some reason functions like dataframe.head() display np.inf as np.nan.
    But it does appear to respect the difference between np.inf and np.nan after
    an HDF5 file is reloaded.

    Note just because google doesn't find a route doesn't mean it can't find a
    route, sometimes you have to try again.  To do so, set the np.inf values you
    want to retry to np.nan.  np.isnan returns True for a np.nan and False for a
    np.inf.

    Parameters
    ----------
    morning_time: integer
        the time when the route leaves the location for SLAC in the morning
        used when departure_time is 'morning', must be in the future

    evening_time: integer
        the time when the route leaves SLAC for location in the evening
        used when departure_time is 'evening', must be in the future

    dataframe: pandas.DataFrame
        used to specify your own data frame
        You probably shouldn't use this parameter.

    Attributes
    ----------
    morning_time: integer
        the time when the route leaves the location for SLAC in the morning
        used when departure_time is 'morning', must be in the future

    evening_time: integer
        the time when the route leaves SLAC for location in the evening
        used when departure_time is 'evening', must be in the future

    SLAC_address: string
        SLAC's address in human-form
        '2575 Sand Hill Rd, Menlo Park, CA 94025'

    SLAC_location: string
        coordinates of SLAC front gate found using google geocoding:
        '37.4200135,-122.203196'

    default_address: string
        a default address useful for testing
        '1543 Oriole Ave, Sunnyvale, CA 94087'

    default_location: string
        coordinates of default_address found using google geocoding:
        '37.342957,-122.0108682'

    column_names: list of strings
        column names used in the DataFrame

    dtypes: dictionary
        dictionary of data types used in the DataFrame

    df: pandas DataFrame
        a pandas DataFrame where all the data work is done

    """
    def __init__(self,morning_time=1551196800,
                      evening_time=1551234600,
                      dataframe=None):
        self.morning_time = morning_time        # depart for work at this time (8:00 AM PST)
        self.evening_time = evening_time        # depart for home at this time (5:30 PM PST)
        self.SLAC_address = '2575 Sand Hill Rd, Menlo Park, CA 94025'
        self.SLAC_location = '37.4200115,-122.203196'
        self.default_address = '1543 Oriole Ave, Sunnyvale, CA 94087' # default
        self.default_location = '37.342957,-122.0108682' # matches the default
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
            temp_df =  pd.read_csv(dataframe,dtype=self.dtypes)
            for col_name in list(temp_df.columns):
                if col_name not in self.column_names:
                    temp_df.drop([col_name],axis='columns')
            return temp_df


    def save_dataframe_csv(self,path_to_csv):
        """saves an open dataframe as a CSV """

        self.df.to_csv(path_to_csv,index=False) # save the file
        self.df = self.open_dataframe(dataframe=None) # replace it in memory


    def check_df(self):
        """
        checks self.df to see if the data has been processed properly
        see self.process_data for how the processing is done

        Parameters
        ----------
        none

        Returns
        -------
        True if processed properly, False otherwise
        """
        def wrap_isint(x):
            return isinstance(x,int)
        id_check = self.df['zillow_id'].apply(wrap_isint).all()
        price_check = self.df['zillow_price'].apply(wrap_isint).all()
        zip_check = self.df['zillow_zipcode'].apply(wrap_isint).all()
        def wrap_isstr(x):
            return isinstance(x,str)
        loc_check = self.df['location'].apply(wrap_isstr).all()
        def wrap_isdt(x):
            return isinstance(x,datetime.datetime)
        dt_check = self.df['date_scraped'].apply(wrap_isdt).all()

        return id_check & price_check & loc_check & dt_check

    def address_to_coords(self,address=None):
        """
        converts a human address into coordinates for directions look-up

        Parameters
        ----------
        address: string
            address string to feed to the Google Geocode API

        Returns
        -------
        unnamed string that the Google API can interpret of the type '1.0,-2.0'
        """
        info_dict = self.gmaps.geocode(address=address)
        if len(info_dict) > 0:
            return info_dict[0]['geometry']['location']
        else:
            return None


    def convert_coords(self,lat=None,lng=None):
        """
        convert coordinates to a string accepted by the gmaps API:
        latitude,longitude

        expected use is:
        self.dataframe['location'] = self.dataframe.apply(lambda row:
                            self.convert_coords(row['lat'],row['lng']),axis=1)

        You can also pass lat as the location dictionary from the Google API.

        Parameters
        ----------
        lat: string or dictionary
            string is the latitude of the GPS coordinates to be converted
            dictionary is a Google API-like dictionary of coordinate
        lng: string
            string is the longitude of the GPS coordinates to be converted
            only used if lat is also a string

        Returns
        -------
        unnamed string that the Google API can interpret of the type '1.0,-2.0'
        """
        # convert the dictionary if necessary
        if isinstance(lat,dict):
            lng = str(lat[u'lng'])
            lat = str(lat[u'lat'])

        if not isinstance(lat,str):
            lat = str(lat)
        if not isinstance(lng,str):
            lng = str(lng)
        return ','.join([lat,lng])


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


    def get_travel_time(self,location=None,departure_time='morning',mode='driving'):
        """
        get directions from location (GPS coordinates) to/from SLAC for driving
        departure_time can be 'morning', 'evening' to use the defaults
        or a time accepted by the API

        Parameters
        ----------
        location: string
            GPS coordinates or address string of the place to or from which
            travel to SLAC will occur.

        departure_time: string
            either 'morning' or 'evening'
            used to define departure_time from the defaults and also switch the
            origin and destination parameters in the Google API.

        mode: string
            either 'driving' or 'transit'
            used to choose travel by car (driving) or by public transit as
            defined in the Google API

        Returns
        -------
        if Google API call is successful:
        unnamed tuple with the following members:
            start_address (string): what Google thinks is the start address
            start_location (string): what Google thinks is the start GPS coords
            end_address (string): what Google thinks is the end address
            end_location (string): what Google thinks is the end GPS coords
            duration (int): time to make the trip
            duration_with_traffic (int): driving time in traffic if mode
                'driving', None if mode 'transit'
        if Google API call is unsuccessful:
            returns None
        """
        if not location: # if the location is None, use the default
            location = self.default_location
        # MARKED FOR DELETION:
        # otherwise check that the origin is entered correctly as a lat,lng string
        # else:
        #     try:
        #         str_check = location.split(',')
        #         float(str_check[0])
        #         float(str_check[1])
        #     except AttributeError:
        #         print('Origin must be a string.')
        #         raise
        #     except ValueError:
        #         print('One of lat or lng cannot be interpreted as a float.  Check location string formatting.')
        #         raise
        #     if len(str_check) != 2:
        #         raise AttributeError('The origin given does not appear to be in the form latitude,longitude.')

        # ensure departure_time is valid
        if departure_time == 'morning':
            departure_time = self.morning_time
            origin = location
            destination = self.SLAC_address
        elif departure_time == 'evening':
            departure_time = self.evening_time
            origin = self.SLAC_address
            destination = location

        else:
            if not isinstance(departure_time,int):
                try:
                    departure_time=int(departure_time)
                except ValueError:
                    print('departure_time must be an integer')
                    raise ValueError

        # check that a valid mode is requested
        if mode not in ['driving','transit']:
            raise ValueError('mode must be either \'driving\' or \'transit\'.')

        #finally call the API!
        # the api says it can't be called with 'transit' and a traffic_model
        # but it doesn't throw an error, so whatever
        info_dict = self.google_dir_wrapper(origin=origin,
                                            destination=destination,
                                            departure_time=departure_time,
                                            mode=mode)

        # print('****************************************************')
        # print('****************************************************')
        # print('Origin: {:s}'.format(location))
        # print('Destination: {:s}'.format(self.SLAC_address))
        # print('departure_time: {:d}'.format(departure_time))
        # print('mode: {:s}'.format(mode))
        # print('****************************************************')
        # print('Returned dictionary:')
        # print(info_dict)
        # print('****************************************************')
        # print('****************************************************')
        if len(info_dict) == 0: # the look up failed
            return None
        # pull out the data for only the first route
        # a unicode string:
        start_address = info_dict[0]['legs'][0]['start_address']
        # a location string (coordinates):
        start_location = self.convert_coords(
                            info_dict[0]['legs'][0]['start_location'])
        # a unicode string:
        end_address = info_dict[0]['legs'][0]['end_address']
        # a location string (coordinates):
        end_location = self.convert_coords(
                            info_dict[0]['legs'][0]['end_location'])
        # an integer, number of seconds:
        duration = info_dict[0]['legs'][0]['duration']['value']
        if mode == 'driving':
            # an integer, number of seconds:
            try:
                duration_in_traffic = info_dict[0]['legs'][0]['duration_in_traffic']['value'] # integer, number of seconds
            except KeyError: # sometimes it doesn't exist for some reason
                duration_in_traffic = np.inf
        else:
            duration_in_traffic = None

        return (start_address,
                start_location,
                end_address,
                end_location,
                duration,
                duration_in_traffic)

    def google_dir_wrapper(self,origin,destination,departure_time,mode):
        """
        call to the Google API directions method with custom error handling.

        Parameters
        ----------
        origin: string
            where the travel starts

        destination: string
            where the travel ends

        departure_time: integer
            time of departure in seconds from January 1, 1970

        mode: string
            travel mode supported by the Google API


        returns
        -------
        the dictionary that the Google API returns
        """

        try:
            info_dict = self.gmaps.directions(origin=origin,
                                              destination=destination,
                                              departure_time=departure_time,
                                              mode=mode,
                                              traffic_model='best_guess')
        except googlemaps.exceptions.Timeout:
            print('Calls to the Google API are being rejected.')
            print('Is it likely you are over your quota.')
            raise googlemaps.exceptions.Timeout
        except googlemaps.exceptions.ApiError:
            print('Human readable address could not be found by the API.')
            print('Typically, this is an address so new Google does not ')
            print('yet know about it.  I will chop off the number and see')
            print('if that works...')
            if origin == self.SLAC_address: # going home
                destination = ' '.join(destination.split(' ')[1:])
            else: # going to SLAC
                origin = ' '.join(origin.split(' ')[1:])
            try:
                info_dict = self.gmaps.directions(origin=origin,
                                                  destination=destination,
                                                  departure_time=departure_time,
                                                  mode=mode,
                                                  traffic_model='best_guess')
            except googlemaps.exceptions.ApiError:
                print('Nope, that did not help.  Returning empty dictionary.')
                return {}

        return info_dict


    def load_files(self,dump_location=None,save_file='saved_data.hdf5'):
        """
        open each of the zipcode files and create one large dataframe

        Parameters
        ----------
        dump_location: string
            the place where input/output files reside

        save_file: string
            name of the hdf5 file to save or open

        Returns
        -------
        nothing
        """
        if not dump_location: # default (None) is to look in /dumped_data/
            dump_location = os.getcwd() +  "/dumped_data/"

        good_load = False
        if save_file in os.listdir(dump_location):
            self.df = pd.read_hdf(dump_location + save_file, key='all_zips')
            good_load = self.check_df() # check to see if the data is possibly correct
            if good_load:
                print('Data loaded successfully from {:s} in {:s}'.format(save_file,dump_location))
        if not good_load:   # iterate through the files in the desired directory
            print('Loading all CSV files in {:s}'.format(dump_location))
            df = self.open_dataframe(None) # create a blank dataframe
            for file_str in os.listdir(dump_location):
                #print 'Opening {:s}'.format(file_str)
                dump_path = dump_location + file_str
                dtf = self.open_dataframe(dump_path)
                if file_str.split('.')[-1] == 'csv': # only open CSV files
                    df = df.append(dtf,ignore_index=True) # append the new dataframe
            self.df = df # update self.dataframe


    def process_data(self):
        """
        Transforms the data in useful ways:

        Keeps only those entries with 'zillow_status' ForSale and RecentlySold
        and that also have a price greater than zero.  Note: as of now all
        RecentlySold houses have a price of zero.  This appears to be because
        they are very old in the zillow database.  It is not a bug.

        Changes 'zillow_id' and 'zillow_zipcode' to be integers.

        Changes 'date_scraped' to be a datetime object.

        Interprets 'zillow_prices' to be integers, including interpreting
        700K -> 700000 and 1.2M -> 1200000.

        Combines 'zillow_longitude' and 'zillow_latitude' into a column named
        location that contains a string concatenation of both that the Google
        API can interpret.

        Makes sure that 'zillow_addressStreet', 'zillow_addressCity' and
        'zillow_addressState' are of type str or unicode.


        Parameters
        ----------
        none

        Returns
        -------
        nothing

        """
        if len(self.df) < 1:
            print 'No data yet loaded.  Run load_files first.'
            return
        elif self.check_df():
            print 'Data already appears processed, skipping this step.'
            return

        # do some filtering of entries we don't want to see
        filter1 = self.df['zillow_status'].isin(['ForSale','RecentlySold']) # only want sales for now
        # it appears that all recently sold have a price of '0'
        filter2 = ~self.df['zillow_price'].isin(['0']) # all prices that are NOT zero
        self.df = self.df[filter1 & filter2] # keep only the desired data

        # turn the zillow_id into an integer
        self.df['zillow_id'] = self.df['zillow_id'].astype(int)

        # turn the zipcode into an integer
        self.df['zillow_zipcode'] = self.df['zillow_zipcode'].astype(int)

        # turn the date scraped in to a datetime
        self.df['date_scraped'] = pd.to_datetime(self.df['date_scraped'])

        # zillow_prices is all screwy with various numbering formats, fix this
        self.df['zillow_price'] = self.df['zillow_price'].apply(self.price_filter)

        # for all the coords, make a string for the google API
        self.df['location'] = self.df.apply(lambda row:
                              self.convert_coords(row['zillow_latitude'],
                              row['zillow_longitude']),axis=1)

        # make sure the address strings are valid
        def wrap_str(x):
            return isinstance(x,(str,unicode))
        mask1 = self.df['zillow_addressStreet'].apply(wrap_str)
        mask2 = self.df['zillow_addressCity'].apply(wrap_str)
        mask3 = self.df['zillow_addressState'].apply(wrap_str)
        mask = mask1 & mask2 & mask3
        self.df = self.df[mask]


    def add_data_to_df(self,index,column,data):
        """
        adds data to self.df at row given by index and column given by column
        if there is already anything but np.nan in that slot it creates a list
        and appends to it
        this function treats the dataframe a bit like a hash table

        Parameters
        ----------
        index: pandas index
            the index of the dataframe row to add data to

        column: string
            the name of the column to add data to

        data: user-defined
            the data to be stored

        Returns
        -------
        nothing, df is modified in place
        """
        if isinstance(self.df.loc[index,column],list): # if a list
            self.df.loc[index,column].append(data) # append the next thing
        elif isinstance(self.df.loc[index,column],(int,float)): # if a number
            # np.nan is a float too
            self.df.loc[index,column] = data # replace it
        elif isinstance(self.df.loc[index,column],(str,unicode)): # if a string
            # strings can collide, make a list
            self.df.at[index,column] = [self.df.loc[index,column],data]


    def get_times(self,number=10):
        """
        Updates rows in the data frame by calling the Google Maps API
        4 times:
        (1) morning drive
        (2) evening drive
        (3) morning transit
        (4) evening transit

        The code looks for np.nan to find durations that have not been tried
        yet.

        If the Google API cannot find a route between the location and SLAC
        the code will fill that duration in with -1.  This means you can't just
        perform self.df['column_name'].mean(), you have to filter for positive
        values first using self.df['column_name'] > 0 (np.nan will be False).

        Parameters
        ----------
        number: integer
            maximum number of calls to the Google API

        Returns
        -------
        calls: integer
            number of times the Google API was called

        """

        calls = 0 # number of calls to the Google API
        row_index = None
        times = ['morning','evening']
        modes = ['driving','transit']
        print('Attempting {:d} calls to the Google API.'.format(number))
        for index,row in self.df.iterrows():
            ds_to_get = [(np.isnan(row['morning_drive_duration']) or
                          np.isnan(row['morning_drive_duration_with_traffic'])),
                         (np.isnan(row['evening_drive_duration']) or
                          np.isnan(row['evening_drive_duration_with_traffic'])),
                          np.isnan(row['morning_transit_duration']),
                          np.isnan(row['evening_transit_duration'])]

            for switch,each in enumerate(ds_to_get):
                if each and calls < number:
                    dep_time = times[switch % 2]
                    mode = modes[0 if switch < 2 else 1]

                    print('Call #{:d} on index {:d}, mode: {:s}, time: {:s}'
                        .format(calls,index,mode,dep_time))
                    address = row['zillow_addressStreet'] + ', ' + \
                              row['zillow_addressCity'] + ', ' + \
                              row['zillow_addressState'] + ' ' + \
                              str(row['zillow_zipcode'])
                    data = self.get_travel_time(location=address,
                                                departure_time=dep_time,
                                                mode=mode)
                    calls += 1
                    if data == None: # this look up failed
                        if mode == 'driving':
                            column = dep_time + '_drive_duration'
                            self.add_data_to_df(index,column,np.inf)
                            column = dep_time + '_drive_duration_with_traffic'
                            self.add_data_to_df(index,column,np.inf)
                        if mode == 'transit':
                            column = dep_time + '_transit_duration'
                            self.add_data_to_df(index,column,np.inf)
                        continue # end this part of the loop

                    tdata = dep_time + ':' + mode + ':' + data[0]
                    self.add_data_to_df(index,'google_start_address',tdata)
                    tdata = dep_time + ':' + mode + ':' + data[1]
                    self.add_data_to_df(index,'google_start_location',tdata)
                    tdata = dep_time + ':' + mode + ':' + data[2]
                    self.add_data_to_df(index,'google_end_address',tdata)
                    tdata = dep_time + ':' + mode + ':' + data[3]
                    self.add_data_to_df(index,'google_end_location',tdata)
                    if mode == modes[0]: #driving
                        column = dep_time + '_drive_duration'
                        self.add_data_to_df(index,column,data[4])
                        column = dep_time + '_drive_duration_with_traffic'
                        self.add_data_to_df(index,column,data[5])
                    if mode == modes[1]: #transit
                        column = dep_time + '_transit_duration'
                        self.add_data_to_df(index,column,data[4])
                        # there is no _with_traffic for transit
        print('Finished calling the Google API.')
        return calls


    def save_dataframe_hdf(self,dump_location=None,save_file='saved_data.hdf5'):
        """
        save the dataframe to an HDF5 file
        ends by closing access to that file

        Parameters
        ----------
        dump_location: string
            the place where input/output files reside

        save_file: string
            name of the hdf5 file to save or open

        Returns
        -------
        nothing
        """
        if not dump_location: # default (None) is to look in /dumped_data/
            dump_location = os.getcwd() +  "/dumped_data/"
        # if the file exists, remove it
        if save_file in os.listdir(dump_location):
            os.remove(dump_location + save_file)
        # create the saved file
        hdf_file = pd.HDFStore(dump_location + save_file)
        hdf_file.put('all_zips',self.df)
        hdf_file.close()


    def find_some_times(self,dump_location=None,save_file='saved_data.hdf5',number=10):
        """
        typical use pattern for finding the travel duration on the penninsula
        WARNING: will overwrite any data you have in memory but not saved

        Parameters
        ----------
        dump_location: string
            the place where input/output files reside

        save_file: string
            name of the hdf5 file to save or open

        number: integer
            maximum number of times to call the Google API

        Returns
        -------
        nothing
        """
        self.load_files(dump_location=dump_location,save_file=save_file)
        self.process_data()
        self.get_times(number=number) # makes number calls to the google API
        self.save_dataframe_hdf(save_file=save_file)
