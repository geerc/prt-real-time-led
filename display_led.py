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
text = "Hello, World"
with open('extracted_api_response.json') as f:
    data = json.load(f)

# List to store the formatted output
formatted_output = []

# Iterate through the list and save the formatted output to the list
for item in data:
    prdtm_last_5 = item['prdtm'][-5:]  # Get the last 5 characters of the 'prdtm' string
    formatted_output.append(f"{item['rt']} {prdtm_last_5}")

print(formatted_output)

# Define the starting position
text_position = (1, 5)  # (x, y) coordinates

# Clear the canvas
canvas.Clear()

# Draw the text
graphics.DrawText(canvas, font, text_position[0], text_position[1], color, text)
# graphics.DrawText(canvas, font, text_position[0], text_position[1], color, text)
# graphics.DrawText(canvas, font, text_position[0], text_position[1], color, text)


# Swap buffers to display the text
matrix.SwapOnVSync(canvas)

# Keep scirpt running until interupted or times out at 100 seconds
try:
    print("Press CTRL-C to stop.")
    while True:
        time.sleep(100)
except KeyboardInterrupt:
    sys.exit(0)
