from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
# from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time
import json
import requests

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'regular'  # or 'adafruit-hat' or 'adafruit-hat-pwm' depending on your setup

# Create the matrix instance
matrix = RGBMatrix(options=options)

# Define colors
color = graphics.Color(255, 255, 255)  # White color

# Create the graphics canvas
canvas = matrix.CreateFrameCanvas()

# Load font
font = graphics.Font()
font.LoadFont("/Users/christiangeer/led-board/prt-real-time-led/rpi-rgb-led-matrix/fonts/4x6.bdf")  # Adjust the path to the font file if needed

# Define static text
# with open('extracted_api_response.json') as f:
#     data = json.load(f)

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
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        # Parse the JSON data from the response
        data = response.json()
    else:
        # return an error message if the request failed
        return f"Failed to retrieve data: {response.status_code}"

    return [{'prdtm': item['prdtm'], 'rt': item['rt'], 'stpnm':item['stpnm'], 'stpid':item['stpid']} for item in data['bustime-response']['prd']]

# filter by stop and format for dispalying
def process_data(data):
    # filter api response by stop id
    homewood_data = [bus for bus in data if bus['stpid'] == '8154']
    fifth_penn_data = [bus for bus in data if bus['stpid'] == '20014']

    # format data into lists of 'rt, prdtm'
    homewood_formatted = [f"{item['rt']} {item['prdtm'][-5:]}" for item in homewood_data]
    fifth_penn_formatted = [f"{item['rt']} {item['prdtm'][-5:]}" for item in fifth_penn_data]

    return homewood_data, fifth_penn_data, homewood_formatted, fifth_penn_formatted

# function to draw homewood stop screen
def draw_homewood(canvas, pos):
    canvas.Clear()

    # Draw the scrolling text at the current position
    scrolling_stop = graphics.DrawText(canvas, font, pos, 5, color, homewood_data[0]['stpnm'])

    # Draw the static text (bus arrival times) - up to 3 lines
    for i in range(min(3, len(homewood_formatted))):  # Limit to the first 3 lines
        graphics.DrawText(canvas, font, 1, 11 + 6 * i, color, homewood_formatted[i])

    return canvas, scrolling_stop

# function to draw fith and penn screen
def draw_fifth_penn(canvas, pos):
    canvas.Clear()

    # Draw the scrolling text at the current position
    scrolling_stop = graphics.DrawText(canvas, font, pos, 5, color, fifth_penn_data[0]['stpnm'])

    # Draw the static text (bus arrival times) - up to 3 lines
    for i in range(min(3, len(fifth_penn_formatted))):  # Limit to the first 3 lines
        graphics.DrawText(canvas, font, 1, 11 + 6 * i, color, fifth_penn_formatted[i])

    return canvas, scrolling_stop

# Initial data fetch and processing
data = fetch_data()
homewood_data, fifth_penn_data, homewood_formatted, fifth_penn_formatted = process_data(data)

# Intitalize poition of the text
pos = canvas.width

# List of screens with their respective scrolling positions
screens = [(draw_homewood, pos), (draw_fifth_penn, pos)]

# Current screen index
current_screen = 0

# Rotation interval in seconds
rotation_interval = 10  # Change screen every 10 seconds

# Time tracking
last_switch_time = time.time()

# Data refresh interval
data_refresh_interval = 30  # Refresh data every 60 seconds
last_refresh_time = time.time()


# Animation loop
while True:
    current_time = time.time()

    # Check if it's time to refresh the data
    if current_time - last_refresh_time >= data_refresh_interval:
        data = fetch_data()
        homewood_data, fifth_penn_data, homewood_formatted, fifth_penn_formatted = process_data(data)
        screens = [(draw_homewood, pos, homewood_data, homewood_formatted), (draw_fifth_penn, pos, fifth_penn_data, fifth_penn_formatted)]
        last_refresh_time = current_time

    # Check if it's time to switch the screen
    if current_time - last_switch_time >= rotation_interval:
        current_screen = (current_screen + 1) % len(screens)
        last_switch_time = current_time

    # Get the current screen function and its scrolling position
    screen_function, pos = screens[current_screen]

    # Draw the current screen with the scrolling text
    canvas, scrolling_stop = screen_function(canvas, pos)

    # Move scrolling text to the left
    pos -= 1

    # Reset position if the text has moved completely off the left side
    if pos + scrolling_stop < 0:
        pos = canvas.width

    # Update the scrolling position in the screens list
    screens[current_screen] = (screen_function, pos)

    # Swap the canvas to update the display
    canvas = matrix.SwapOnVSync(canvas)

    # Delay to control the speed of the scrolling
    time.sleep(0.05)

# Swap buffers to display the text
matrix.SwapOnVSync(canvas)

# Keep scirpt running until interupted or times out at 100 seconds
try:
    print("Press CTRL-C to stop.")
    while True:
        time.sleep(100)
except KeyboardInterrupt:
    sys.exit(0)
