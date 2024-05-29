from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
# from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time
import json

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

# Define the text
# text = "Hello, World"
with open('extracted_api_response.json') as f:
    data = json.load(f)

# filter api response by stop id
homewood_data = [bus for bus in data if bus['stpid'] == '8154']
fifth_penn_data = [bus for bus in data if bus['stpid'] == '20014']
print('Homewood data:  ', homewood_data[0]['stpnm'])
# Lists to store the formatted output
homewood_formatted = []
fifth_penn_formatted = []

# Iterate through the list and save the formatted output to the list
for item in homewood_data:
    prdtm_last_5 = item['prdtm'][-5:]  # Get the last 5 characters (time) of the 'prdtm' string
    homewood_formatted.append(f"{item['rt']} {prdtm_last_5}")

for item in fifth_penn_data:
    prdtm_last_5 = item['prdtm'][-5:]  # Get the last 5 characters (time) of the 'prdtm' string
    fifth_penn_formatted.append(f"{item['rt']} {prdtm_last_5}")

print('Homewood output: ', homewood_formatted)
print('Fifth output: ', fifth_penn_formatted)

# Save stop name to variable

# function to draw homewood stop screen
def draw_homewood(canvas, pos):
    canvas.Clear()

    # Draw the scrolling text at the current position
    scrolling_stop = graphics.DrawText(canvas, font, pos, 5, color, homewood_data[0]['stpnm'])

    # Draw the static text
    graphics.DrawText(canvas, font, 1, 11, color, homewood_formatted[0])
    graphics.DrawText(canvas, font, 1, 17, color, homewood_formatted[1])
    graphics.DrawText(canvas, font, 1, 23, color, homewood_formatted[2])

    return canvas, scrolling_stop

# function to draw fith and penn screen
def draw_fifth_penn(canvas, pos):
    canvas.Clear()

    # Draw the scrolling text at the current position
    scrolling_stop = graphics.DrawText(canvas, font, pos, 5, color, fifth_penn_data[0]['stpnm'])

    # Draw the static text
    graphics.DrawText(canvas, font, 1, 11, color, fifth_penn_formatted[0])
    graphics.DrawText(canvas, font, 1, 17, color, fifth_penn_formatted[1])

    return canvas, scrolling_stop


# Intitalize poition of the text
pos = canvas.width

# List of screens with their respective scrolling positions
screens = [(draw_homewood, pos), (draw_fifth_penn, pos)]

# Current screen index
current_screen = 0

# Rotation interval in seconds
rotation_interval = 10  # Change screen every 5 seconds

# Time tracking
last_switch_time = time.time()

# Animation loop
while True:
    current_time = time.time()

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
