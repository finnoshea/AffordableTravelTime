# AffordableTravelTime
Affordability versus travel time for the peninsula

Requires a file in the root directory named 'credentials.json' with the following content:

`{"gmap_key": "YOUR_API_KEY_HERE"}`

Also recommended that you have pandas 24.3 or newer to take advantage of ignoring np.inf in the same way as np.nan.

Typical use of google_api.py:
import google_api
t = ATTGoogleAPI()
t.find_some_times(number=100)
