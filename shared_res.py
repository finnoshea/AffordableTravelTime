#!/usr/bin/env python
"""Shared resources, so that commonly used information is all in one place.
"""

__license__ = "GPL"
__version__ = "0.0"
__status__ = "Development"

import numpy as np

# names of the columns in the pandas dataframe
pandas_column_names = ['zillow_id',
                       'zillow_addressStreet',
                       'zillow_addressCity',
                       'zillow_addressState',
                       'zillow_zipcode',
                       'zillow_features',
                       'zillow_price',
                       'zillow_longitude',
                       'zillow_latitude',
                       'zillow_status',
                       'zillow_homeType',
                       'zillow_days_on',
                       'date_scraped',
                       'location',
                       'google_start_address',
                       'google_start_location',
                       'google_end_address',
                       'google_end_location',
                       'morning_drive_duration',
                       'morning_drive_duration_with_traffic',
                       'evening_drive_duration',
                       'evening_drive_duration_with_traffic',
                       'morning_transit_duration',
                       'evening_transit_duration']

# all the travel times are integer numbers of seconds, but numpy can't handle
# NaNs in int64, so make them floats
# see: http://pandas.pydata.org/pandas-docs/stable/gotchas.html#support-for-integer-na
pandas_dtypes = {'zillow_id': np.int64,
                 'zillow_addressStreet': np.str,
                 'zillow_addressCity': np.str,
                 'zillow_addressState': np.str,
                 'zillow_zipcode': np.int64,
                 'zillow_features': np.str,
                 'zillow_price': np.str,
                 'zillow_longitude': np.float64,
                 'zillow_latitude': np.float64,
                 'zillow_status': np.str,
                 'zillow_homeType': np.str,
                 'zillow_days_on': np.int64,
                 'date_scraped': np.str,
                 'location': np.str,
                 'google_start_address': np.str,
                 'google_start_location': np.str,
                 'google_end_address': np.str,
                 'google_end_location': np.str,
                 'morning_drive_duration': np.float64,
                 'morning_drive_duration_with_traffic': np.float64,
                 'evening_drive_duration': np.float64,
                 'evening_drive_duration_with_traffic': np.float64,
                 'morning_transit_duration': np.float64,
                 'evening_transit_duration': np.float64}

# Grabbed from http://www.city-data.com/county/Santa_Clara_County-CA.html
santa_clara_county_zip ='\
94022 \
94023 \
94024 \
94040 \
94041 \
94042 \
94043 \
94085 \
94086 \
94087 \
94089 \
94301 \
94304 \
94305 \
94306 \
95002 \
95008 \
95014 \
95020 \
95030 \
95031 \
95032 \
95033 \
95035 \
95037 \
95038 \
95046 \
95050 \
95051 \
95054 \
95056 \
95070 \
95108 \
95110 \
95111 \
95112 \
95113 \
95116 \
95117 \
95118 \
95119 \
95120 \
95121 \
95122 \
95123 \
95124 \
95125 \
95126 \
95127 \
95128 \
95129 \
95130 \
95131 \
95132 \
95133 \
95134 \
95135 \
95136 \
95138 \
95139 \
95140 \
95148 \
95150 \
95151 \
95158 \
95160 \
95164'
santa_clara_county_zip = santa_clara_county_zip.split(' ')


# http://www.city-data.com/county/Santa_Cruz_County-CA.html
santa_cruz_county_zip = '\
95001 \
95003 \
95005 \
95006 \
95010 \
95017 \
95018 \
95019 \
95060 \
95061 \
95062 \
95063 \
95064 \
95065 \
95066 \
95067 \
95073 \
95076'
santa_cruz_county_zip = santa_cruz_county_zip.split(' ')

# http://www.city-data.com/county/San_Mateo_County-CA.html
san_mateo_county_zip = '\
94002 \
94005 \
94010 \
94014 \
94015 \
94018 \
94019 \
94020 \
94021 \
94025 \
94026 \
94027 \
94028 \
94029 \
94030 \
94037 \
94038 \
94044 \
94060 \
94061 \
94062 \
94063 \
94065 \
94066 \
94070 \
94074 \
94080 \
94128 \
94303 \
94401 \
94402 \
94403 \
94404'
san_mateo_county_zip = san_mateo_county_zip.split(' ')

# http://www.city-data.com/county/San_Francisco_County-CA.html
san_francisco_county_zip ='\
94101 \
94102 \
94103 \
94104 \
94105 \
94107 \
94108 \
94109 \
94110 \
94111 \
94112 \
94114 \
94115 \
94116 \
94117 \
94118 \
94119 \
94121 \
94122 \
94123 \
94124 \
94127 \
94129 \
94131 \
94132 \
94133 \
94134 \
94137 \
94142 \
94188'
san_francisco_county_zip = san_francisco_county_zip.split(' ')

# http://www.city-data.com/county/Alameda_County-CA.html
alameda_county_zip = '\
94501 \
94502 \
94536 \
94538 \
94539 \
94541 \
94542 \
94544 \
94545 \
94546 \
94550 \
94551 \
94552 \
94555 \
94560 \
94566 \
94568 \
94577 \
94578 \
94579 \
94580 \
94582 \
94586 \
94587 \
94588 \
94601 \
94602 \
94603 \
94605 \
94606 \
94607 \
94608 \
94609 \
94610 \
94611 \
94612 \
94618 \
94619 \
94621 \
94650 \
94702 \
94703 \
94704 \
94705 \
94706 \
94707 \
94708 \
94709 \
94710'
alameda_county_zip = alameda_county_zip.split(' ')

# http://www.city-data.com/county/Contra_Costa_County-CA.html
contra_costa_county_zip = '\
94506 \
94507 \
94509 \
94511 \
94513 \
94514 \
94516 \
94517 \
94518 \
94519 \
94520 \
94521 \
94523 \
94524 \
94525 \
94526 \
94528 \
94530 \
94531 \
94547 \
94549 \
94553 \
94556 \
94561 \
94563 \
94564 \
94565 \
94583 \
94595 \
94596 \
94597 \
94598 \
94801 \
94803 \
94804 \
94805 \
94806'
contra_costa_county_zip = contra_costa_county_zip.split(' ')

# http://www.city-data.com/county/Marin_County-CA.html
marin_county_zip = '\
94901 \
94903 \
94904 \
94920 \
94924 \
94925 \
94930 \
94933 \
94937 \
94939 \
94941 \
94942 \
94945 \
94946 \
94947 \
94949 \
94950 \
94956 \
94957 \
94960 \
94965 \
94970 \
94973 \
94979'
marin_county_zip = marin_county_zip.split(' ')

# http://www.city-data.com/county/Solano_County-CA.html
solano_county_zip ='\
94510 \
94533 \
94534 \
94571 \
94585 \
94589 \
94590 \
94591 \
95620 \
95687 \
95688'
solano_county_zip = solano_county_zip.split(' ')

# http://www.city-data.com/county/Sonoma_County-CA.html
sonoma_county_zip ='\
94927 \
94928 \
94931 \
94951 \
94952 \
94954 \
95401 \
95402 \
95403 \
95404 \
95405 \
95407 \
95409 \
95416 \
95425 \
95436 \
95439 \
95442 \
95446 \
95448 \
95452 \
95471 \
95472 \
95473 \
95476 \
95486 \
95492 \
95497'
sonoma_county_zip = sonoma_county_zip.split(' ')

# http://www.city-data.com/county/Napa_County-CA.html
napa_county_zip = '\
94503 \
94508 \
94515 \
94558 \
94559 \
94574 \
94581 \
94599'
napa_county_zip = napa_county_zip.split(' ')

# http://www.city-data.com/county/San_Joaquin_County-CA.html
san_joaquin_county_zip ='\
95204 \
95205 \
95206 \
95207 \
95209 \
95210 \
95212 \
95215 \
95219 \
95220 \
95227 \
95236 \
95237 \
95240 \
95242 \
95258 \
95269 \
95290 \
95304 \
95320 \
95330 \
95336 \
95337 \
95366 \
95376 \
95377'
san_joaquin_county_zip = san_joaquin_county_zip.split(' ')
