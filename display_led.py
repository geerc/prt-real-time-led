from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
# from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
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
font.LoadFont("../../fonts/7x13.bdf")  # Adjust the path to the font file if needed

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

# Keep the text displayed for a certain time (e.g., 10 seconds)
time.sleep(10)

# Optionally clear the matrix after displaying the text
matrix.Clear()
