import time
import board
import pygame
from adafruit_apds9960.apds9960 import APDS9960
from adafruit_apds9960 import colorutility

# Initialize Pygame for audio playback
pygame.mixer.init()

# Function to play music
def play_music(mp3_file):
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()  # Stop any currently playing music
    pygame.mixer.music.load(mp3_file)
    pygame.mixer.music.play()

# Function to stop music
def stop_music():
    pygame.mixer.music.stop()

def classify_color(r, g, b):
    # Normalize RGB values
    total = r + g + b
    if total == 0:
        return "Unknown"  # Avoid division by zero

    rn = r / total
    gn = g / total
    bn = b / total

    if r < 50 and g < 50 and b < 50:
        return "Black"
    elif bn > 0.5 and bn > rn + 0.2 and bn > gn + 0.2:
        return "Blue"

    diff_rg = abs(r - g)
    diff_rb = abs(r - b)
    
    if total > 5000: 
        return "Unknown"

    if r > 1000 and diff_rg < 1000 and diff_rb > 700:
        # return "Orange"
        return "Red"
    elif r > 500 and diff_rg > 500 and diff_rb > 400:
        return "Red" 
    
    return "Unknown"

color_music_map = {
    'Blue': 'blue.mp3',
    'Orange': 'Flirting With June-Les Gordon.mp3',
    'Black': 'back_in_black.mp3',
    'Red': 'red.mp3'
}

i2c = board.I2C()
apds = APDS9960(i2c)
apds.enable_color = True

last_color = None
last_change_time = time.time()
stable_time = 1  # seconds
currently_playing = None

while True:
    while not apds.color_data_ready:
        time.sleep(0.005)

    r, g, b, c = apds.color_data
    color = classify_color(r, g, b)

    current_time = time.time()

    if color != last_color:
        last_color = color
        last_change_time = current_time
        print(f"Color changed to {color}")

    if current_time - last_change_time > stable_time:
        if color in color_music_map and color != currently_playing:
            print(f"Stable color detected: {color}, playing music.")
            play_music(color_music_map[color])
            currently_playing = color
    elif currently_playing and current_time - last_change_time <= stable_time:
        stop_music()
        currently_playing = None

    print(f"Detected Color: {color}")
    print(f"RGB Values: R={r}, G={g}, B={b}")
    print(f"Color Temperature: {colorutility.calculate_color_temperature(r, g, b)} K")
    print(f"Light Lux: {colorutility.calculate_lux(r, g, b)}")

    time.sleep(1)
