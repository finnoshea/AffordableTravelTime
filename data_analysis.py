#!/usr/bin/env python
"""Data analysis main file.
"""

__license__ = "GPL"
__version__ = "0.0"
__status__ = "Development"

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

# Fixing random state for reproducibility
np.random.seed(19680801)

t = pd.read_hdf('./dumped_data/saved_data.hdf5',key='all_zips')

# Principal is the initial loan amount.
# interest is the MONTHLY interest.  i.e. is the yearly interst is 4% then
# interest = 0.04/12
# months is the length of the loans in months.
def calculate_monthly_payment(principal, interest, months):
    monthly_payment = principal * \
                      (interest * (1 + interest)**months) / \
                      ((1+interest)**months - 1)
    return(monthly_payment)

def process_data(t):
    """
    adds useful features to t
    """

    # price in mega-bucks
    t['price (M$)'] = t['zillow_price'] / 1000000.0
    # averge times in minutes
    t['average_drive_duration'] = \
        t['morning_drive_duration'].add(t['evening_drive_duration']).div(120.0)
    t['average_drive_duration_with_traffic'] = \
            t['morning_drive_duration_with_traffic'] \
                .add(t['evening_drive_duration_with_traffic']).div(120.0)
    t['average_transit_duration'] = \
            t['morning_transit_duration'] \
                .add(t['evening_transit_duration']).div(120.0)
    # identify east bay locations
    t['east_bay'] = t['location'].apply(find_east_bay)

    # filter for < 180 minute drives in traffic, < $5M and SINGLE_FAMILY homes
    mask = (t['average_drive_duration_with_traffic'] < 180) & \
           (t['price (M$)'] < 5) & \
           (t['zillow_homeType'] == 'SINGLE_FAMILY')

    return t[mask]

def find_east_bay(lat=0.0,lng=0.0):
    """
    accepts lat and lng and tells you if the property is in the east bay

    Parameters
    ----------
    lat: float or string
        if float, latitude you want to check (requires a longitude)
        if string, a string of the form 1.234,5.678 for use with pandas apply
        latitude comes first in this string
    lng: float
        longitude you want to check

    Returns
    -------
    boolean
        True if the location is in the east bay
    """
    # check for the string
    if isinstance(lat,(str,unicode)):
        tl = lat.split(',')
        lat = float(tl[0])
        lng = float(tl[1])
    # a GPS point near Treasure Island
    x1 = -122.389807
    y1 = 37.813489
    # a GPS point just north of San Jose
    x2 = -121.986697
    y2 = 37.418685
    if lat < y2: # anything south of San Jose is not in the east bay
        return False
    val = (lng - x1) * (y2 - y1) - (lat - y1) * (x2 - x1)
    # positive values are east bay, negative values are peninsula
    return val > 0


t = process_data(t)
################################################################################
# you can make pretty plots now
################################################################################

def price_dist_plot():
    """
    plot of price versus distance

    """
    plt.figure(22)
    # plot the east bay points
    eb_mask = t['east_bay']
    plt.scatter(x=t['price (M$)'][eb_mask],
                y=t['average_drive_duration_with_traffic'][eb_mask],
                s=5,
                c='b',
                marker='.')
    # plot the not east bay points
    neb_mask = ~t['east_bay']
    plt.scatter(x=t['price (M$)'][neb_mask],
                y=t['average_drive_duration_with_traffic'][neb_mask],
                s=5,
                c='r',
                marker='.')
    plt.xlabel('commute time to SLAC (min)')
    plt.ylabel('price (M$)')
    plt.title('Single family homes, <$5M and <180 mins')
    plt.show()


def plot_by_zipcode():
    """
    plots the results for single family homes by zipcode
    """
    # find all the unique zipcodes
    zipcodes = t['zillow_zipcode'].unique()
    colors = np.random.rand(len(zipcodes),3)
    plt.figure(23)
    for i,zipcode in enumerate(zipcodes):
        temp = t[t['zillow_zipcode']==zipcode]
        x = temp['price (M$)']
        y = temp['average_drive_duration_with_traffic']
        plt.scatter(x=x,y=y,s=5,marker='.',c=colors[i],label=str(zipcode))
    plt.xlabel('commute time to SLAC (min)')
    plt.ylabel('price (M$)')
    plt.title('Single family homes, <$5M and <180 mins')
    plt.legend(loc='upper right')
    plt.show()


def dbscan_price_drive(epsilon=0.1,min_samples=50):
    """
    DBSCAN cluster analysis of the data in terms of price and
    average_drive_duration_with_traffic
    """
    tt = t[['price (M$)','average_drive_duration_with_traffic']]
    scaler = StandardScaler()
    ts = scaler.fit_transform(tt)
    db = DBSCAN(eps=epsilon, min_samples=min_samples).fit(ts)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_
    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)
    print('Estimated number of clusters: %d' % n_clusters_)
    print('Estimated number of noise points: %d' % n_noise_)
    # Black removed and is used for noise instead.
    unique_labels = set(labels)
    colors = [plt.cm.Spectral(each)
              for each in np.linspace(0, 1, len(unique_labels))]
    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Black used for noise.
            col = [0, 0, 0, 1]

        class_member_mask = (labels == k)

        x = tt.loc[:,'price (M$)'][class_member_mask & core_samples_mask]
        y = tt.loc[:,'average_drive_duration_with_traffic'][class_member_mask & core_samples_mask]
        plt.plot(x[:],y[:], 'o', markerfacecolor=tuple(col),
                 markeredgecolor='k', markersize=10)

        x = tt.loc[:,'price (M$)'][class_member_mask & ~core_samples_mask]
        y = tt.loc[:,'average_drive_duration_with_traffic'][class_member_mask & ~core_samples_mask]
        plt.plot(x[:],y[:], 'o', markerfacecolor=tuple(col),
                 markeredgecolor='k', markersize=2)

    plt.title('Estimated number of clusters: %d' % n_clusters_)
    plt.show()




















# END ##########################################################################
