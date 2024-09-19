from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
# from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time
import json
import requests
import os
from PIL import Image
from datetime import datetime, timedelta
import pandas as pd

# Load the config file
with open('config.json') as f:
    config = json.load(f)

# Extract matrix options from the config file
matrix_config = config['matrix_options']

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = matrix_config.get('rows', 32)  # Default to 32 if not specified
options.cols = matrix_config.get('cols', 64)  # Default to 64 if not specified
options.chain_length = matrix_config.get('chain_length', 1)
options.parallel = matrix_config.get('parallel', 1)
options.hardware_mapping = matrix_config.get('hardware_mapping', 'adafruit-hat')
options.gpio_slowdown = matrix_config.get('gpio_slowdown', 4)

# Create the matrix instance
matrix = RGBMatrix(options=options)

# Define colors
color = graphics.Color(255, 255, 255)  # White color

# Create the graphics canvas
canvas = matrix.CreateFrameCanvas()

# Load font
font = graphics.Font()
font.LoadFont("/Users/christiangeer/led-board/prt-real-time-led/rpi-rgb-led-matrix/fonts/4x6.bdf")  # Adjust the path to the font file if needed
# font.LoadFont("/home/christiangeer/prt-real-time-led/rpi-rgb-led-matrix/fonts/4x6.bdf")

# Define colors
predicted_color = graphics.Color(0, 255, 0)  # Green for predicted times
scheduled_color = graphics.Color(255, 255, 255)  # White for scheduled times

# define api endpoint url
api_url = 'http://realtime.portauthority.org/bustime/api/v3/getpredictions'

# Define parameters for api call
params = {
    'key': '7Cjew3Pd88mihr5aDsA2R3yyF',
    'stpid': '20014,8154',
    'format': 'json',
    'rtpidatafeed':'Port Authority Bus'}

# function to retrieve api response
def fetch_data():
    # Load API parameters from the config file
    api_params = stops_config['api_params']

    # Build the 'stpid' parameter by joining stop IDs from the config
    stpid = ','.join([stop['id'] for stop in stops_config['stops']])

    # Add the dynamic 'stpid' parameter to the api_params dictionary
    api_params['stpid'] = stpid

    # Send the GET request with the dynamically set parameters
    response = requests.get(api_url, params=api_params)

    if response.status_code == 200:
        # Parse the JSON data from the response
        data = response.json()
    else:
        # return an error message if the request failed
        return f"Failed to retrieve data: {response.status_code}"

    return [{'prdtm': item['prdtm'], 'rt': item['rt'], 'stpnm':item['stpnm'], 'stpid':item['stpid']} for item in data['bustime-response']['prd']]

# Load the image
image_path = "/Users/christiangeer/led-board/prt-real-time-led/img/bus.png"
if not os.path.isfile(image_path):
    raise FileNotFoundError(f"Image file not found: {image_path}")

desired_width = 25
desired_height = 25
image = Image.open(image_path)
image = image.resize((desired_width, desired_height))
image = image.convert('RGB')

# Function to draw the image on the canvas
def draw_image_on_canvas(canvas, x, y):
    for ix in range(image.width):
        for iy in range(image.height):
            r, g, b = image.getpixel((ix, iy))
            canvas.SetPixel(x + ix, y + iy, r, g, b)

# filter by stop and format for output
def process_data(data):
    def to_12hr_format(time_str):
        # Convert the string time to 12-hour format
        time_24hr = datetime.strptime(time_str, "%Y%m%d %H:%M")
        return time_24hr.strftime("%I:%M")

    def is_future_time(time_str):
        # Convert the time string to datetime object
        time_24hr = datetime.strptime(time_str, "%Y%m%d %H:%M")
        # Check if the time is at least 10 minutes in the future compared to current time
        return time_24hr > datetime.now() + timedelta(minutes=10)

    # Dictionary to store the formatted data by stop name
    formatted_data = {}

    # Iterate through each stop from the configuration file
    for stop in config['stops']:
        # Filter the bus data for this stop based on stop ID and ensure it's 10 minutes or more in the future
        stop_data = [bus for bus in data if bus['stpid'] == stop['id'] and is_future_time(bus['prdtm'])]

        # If there is data for this stop, proceed
        if stop_data:
            # Get the stop name from the first bus data (all buses for this stop have the same stop name)
            stop_name = stop_data[0]['stpnm']

            # Format each bus entry as "route_number arrival_time", and add to the dictionary
            formatted_data[stop_name] = [f"{item['rt']} {to_12hr_format(item['prdtm'])}" for item in stop_data]

    # Return the formatted data where the key is the stop name and the value is a list of buses
    return formatted_data


# Function to draw a stop's data on the LED matrix
def draw_stop(canvas, pos, stop_name, stop_formatted, stop_data):
    canvas.Clear()

    # Draw the image
    draw_image_on_canvas(canvas, 37, 5)

    # Draw the scrolling text at the current position
    scrolling_stop = graphics.DrawText(canvas, font, pos, 5, color, stop_name)

    # Draw the static text (bus arrival times) - up to 3 lines
    for i in range(min(3, len(stop_formatted))):  # Limit to the first 3 lines
        graphics.DrawText(canvas, font, 1, 11 + 6 * i, color, stop_formatted[i])

    return canvas, scrolling_stop, stop_formatted


# Initial data fetch and processing
data = fetch_data()
formatted_data = process_data(data)

# Initialize position of the text
pos = canvas.width

# Create a list of screens dynamically based on the stops in the config file
screens = [
    (stop['name'], pos, formatted_data[stop['name']])
    for stop in config['stops']
]

# Current screen index
current_screen = 0

# Rotation interval in seconds
rotation_interval = 10  # Change screen every 10 seconds

# Time tracking
last_switch_time = time.time()

# Data refresh interval
data_refresh_interval = 30  # Refresh data every 30 seconds
last_refresh_time = time.time()

# Animation loop
while True:
    current_time = time.time()

    # Check if it's time to refresh the data
    if current_time - last_refresh_time >= data_refresh_interval:
        data = fetch_data()
        formatted_data = process_data(data)
        # Update the screens list with the new data
        screens = [
            (stop['name'], pos, formatted_data[stop['name']])
            for stop in config['stops']
        ]
        last_refresh_time = current_time

    # Check if it's time to switch the screen
    if current_time - last_switch_time >= rotation_interval:
        current_screen = (current_screen + 1) % len(screens)
        last_switch_time = current_time

    # Get the current stop's data
    stop_name, pos, stop_formatted = screens[current_screen]

    # Draw the current stop's screen with the scrolling text
    canvas, scrolling_stop, stop_formatted = draw_stop(canvas, pos, stop_name, stop_formatted, stop_formatted)

    # Move scrolling text to the left
    pos -= 1

    # Reset position if the text has moved completely off the left side
    if pos + scrolling_stop < 0:
        pos = canvas.width

    # Draw the current stop's screen with the scrolling text
    canvas, scrolling_stop, stop_formatted = draw_stop(canvas, pos, stop_name, stop_formatted, stop_formatted)

    # Swap the canvas to update the display
    canvas = matrix.SwapOnVSync(canvas)

    # Delay to control the speed of the scrolling
    time.sleep(0.05)

# Swap buffers to display the text
matrix.SwapOnVSync(canvas)

# Keep script running until interrupted or times out at 100 seconds
try:
    print("Press CTRL-C to stop.")
    while True:
        time.sleep(100)
except KeyboardInterrupt:
    sys.exit(0)
