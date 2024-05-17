from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
# from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 64
options.cols = 32
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
font.LoadFont("/Users/christiangeer/led-board/prt-real-time-led/rpi-rgb-led-matrix/fonts/7x13.bdf")  # Adjust the path to the font file if needed

# Define the text
text = "Hello, World!"

# Define the starting position
text_position = (10, 20)  # (x, y) coordinates

# Clear the canvas
canvas.Clear()

# Draw the text
graphics.DrawText(canvas, font, text_position[0], text_position[1], color, text)

# Swap buffers to display the text
matrix.SwapOnVSync(canvas)

# Keep scirpt running until interupted or times out at 100 seconds
try:
    print("Press CTRL-C to stop.")
    while True:
        time.sleep(100)
except KeyboardInterrupt:
    sys.exit(0)
