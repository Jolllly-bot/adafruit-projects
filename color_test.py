import time
import board
from adafruit_apds9960.apds9960 import APDS9960
from adafruit_apds9960 import colorutility

def classify_color(r, g, b):
    # Normalize RGB values
    total = r + g + b
    if total == 0:
        return "Unknown"  # Avoid division by zero, assume sensor sees very little light

    # Calculate normalized RGB
    rn = r / total
    gn = g / total
    bn = b / total

    # Define thresholds for black and blue using normalized values
    if r < 50 and g < 50 and b < 50:
        return "Black"
    elif bn > 0.5 and bn > rn + 0.2 and bn > gn + 0.2:
        return "Blue"

    # Define thresholds for orange and red using absolute differences
    diff_rg = abs(r - g)
    diff_rb = abs(r - b)
    
    # Adjust thresholds based on real-world data for distinguishing orange and red
    if total > 5000:  # This threshold might need adjustment based on your typical sensor readings
        return "Unknown"

    if r > 1000 and diff_rg < 1000 and diff_rb > 700:
        return "Orange"
    elif r > 500 and diff_rg > 500 and diff_rb > 400:
        return "Red" 
    
    return "Unknown"

i2c = board.I2C()
apds = APDS9960(i2c)
apds.enable_color = True

while True:
    # Wait for color data to be ready
    while not apds.color_data_ready:
        time.sleep(0.005)

    # Get the color data from the sensor
    r, g, b, c = apds.color_data
    color = classify_color(r, g, b)

    # Print the detected color and sensor readings
    print(f"Detected Color: {color}")
    print(f"RGB Values: R={r}, G={g}, B={b}")
    print(f"Color Temperature: {colorutility.calculate_color_temperature(r, g, b)} K")
    print(f"Light Lux: {colorutility.calculate_lux(r, g, b)}")

    time.sleep(1)
