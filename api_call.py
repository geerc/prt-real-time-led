import requests

# Define the url
url = 'http://realtime.portauthority.org/bustime/api/v3/getpredictions'


# Define parameters
params = {
    'key': '7Cjew3Pd88mihr5aDsA2R3yyF',
    'stpid': 8154,
    'rt': 'P1',
    'format': 'json',
    'rtpidatafeed':'Port Authority Bus'}


# Make the GET request with parameters
response = requests.get(url, params=params)

if response.status_code == 200:
    # Parse the JSON data from the response
    data = response.json()
    # Print the data (or handle it as needed)
    print(data)
else:
    # Print an error message if the request failed
    print(f"Failed to retrieve data: {response.status_code}")
