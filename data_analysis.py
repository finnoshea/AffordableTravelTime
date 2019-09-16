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
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from sklearn.gaussian_process.kernels import DotProduct, WhiteKernel
plt.ion()

# Fixing random state for reproducibility
np.random.seed(19680801)

# A function to use a Gaussian Process Regressor to extrapolate travel time
# data from one data set to others. Travel time comes from Google Maps which
# costs money. We want to avoid paying for more API calls when we already
# have plenty of travel time data.
def GP_Winter_2018_Travel_Time_data(diagnostic_on):
    '''
    # A function to use a Gaussian Process Regressor to extrapolate travel time
    # data from one data set to others. Travel time comes from Google Maps which
    # costs money. We want to avoid paying for more API calls when we already
    # have plenty of travel time data.
    :param diagnostic_on: Turn on test/diagnostics and plots
    :return:
    '''
    # This is a local path that wont be shared to preserve data.
    Winter_2018 = pd.read_hdf(
        "../../travel_time_data/Winter_2018_Travel_Time.hdf5")
    # Turn the data into np.arrays that are easier to handle instead of
    # typing the dataframe names over and over.
    X = Winter_2018[['zillow_longitude', 'zillow_latitude']].values
    Y = Winter_2018['morning_drive_duration_with_traffic'].values
    # Reduce the dimensionality to fit so it isn't so slow!
    N = 2 ** 10
    points = np.sort(np.random.randint(0, len(X) - 1, N))
    x = X[points]
    y = Y[points]
    print('Fitting the 2D GP model...')
    # Specify the kernel
    kernel = C(np.mean(y)) + RBF((0.02, 0.02), (1e-5, 1e+2)) \
             + WhiteKernel(1.0, noise_level_bounds=(1e-10, 1e+0))
    gpr = GaussianProcessRegressor(kernel=kernel,
                                   alpha=1e-3,
                                   n_restarts_optimizer=1)
    # Fit the known data
    gpr.fit(x, y)

    # Diagnostic checks
    if diagnostic_on == 1:
        # Predict on the data that wasn't used to fit.
        T = np.linspace(0, len(X) - 1, len(X), dtype='int')
        xx = X[~np.isin(T, points)]
        yy = Y[~np.isin(T, points)]
        print('Predicting using 2D GP model...')
        y_pred = gpr.predict(xx)

        # Calculate the absolute prediction error
        pred_error = np.divide((yy - y_pred), yy)
        print('The mean error is %.3f' % np.mean(pred_error))
        # Calculate the absolute prediction error
        pred_error = np.divide((yy - y_pred), yy)
        print('The mean error is %.3f' % np.mean(pred_error))

        # Use a subset of points so the plot doesn't murder your computer.
        N = 2 ** 9
        subset = np.sort(np.random.randint(0, len(yy) - 1, N))
        yy_subset = yy[subset]
        y_pred_subset = y_pred[subset]

        plt.close(1)
        fig = plt.figure(1)
        fig.set_facecolor('white')
        ax1 = fig.add_subplot(111)
        ax1.plot(yy_subset, y_pred_subset, 'r.')
        ax1.set_xlim([0, 10000])
        ax1.set_ylim([0, 10000])
        ax1.set_xlabel("Google Maps Travel Time [s]", fontsize=20)
        ax1.set_ylabel("GP Predicted Travel Time [s]", fontsize=20)



# Test out the GP import
if __name__ == '__main__':
    GP_Winter_2018_Travel_Time_data(1)





# END ##########################################################################
