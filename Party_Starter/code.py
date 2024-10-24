import time
import random
from adafruit_circuitplayground import cp

# Global variables for game state
player_count = 1  # Start with one player
player_colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(10)]  # Initial colors
turn_duration = 5  # Initial turn duration set to 10 seconds


def spin_wheel():
    spin_time = random.randint(5, 10)
    end_time = time.monotonic() + spin_time
    current_led = 0
    speed = 0.1

    while time.monotonic() < end_time:
        cp.pixels.fill((0, 0, 0))
        cp.pixels[current_led] = player_colors[current_led]
        time.sleep(speed)
        current_led = (current_led + 1) % player_count
        if speed < 0.5:
            speed *= 1.05

    chosen_led = random.randint(0, player_count - 1)
    cp.pixels.fill((0, 0, 0))
    cp.pixels[chosen_led] = player_colors[chosen_led]
    time.sleep(2)

def hot_potato():
    cp.pixels.brightness = 0.3
    potato_time = max(5, 2 * player_count)
    start_time = time.monotonic()
    end_time = start_time + potato_time
    initial_leds = 10

    cp.pixels.fill((255, 165, 0))  # Starting color for Hot Potato

    while time.monotonic() < end_time:
        elapsed = time.monotonic() - start_time
        leds_on = initial_leds - int((elapsed / potato_time) * initial_leds)
        if leds_on < 1:
            leds_on = 1
        
        cp.pixels.fill((0, 0, 0))  # Clear LEDs
        for i in range(leds_on):
            cp.pixels[i] = (255, 165, 0)
        time.sleep(0.1)

    cp.pixels.fill((255, 0, 0))  # Indicate the end with red LEDs
    for _ in range(3):
        cp.play_tone(1000, 0.4)
        time.sleep(0.1)
    cp.pixels.fill((0, 0, 0))

def update_player_count():
    global player_count
    cp.pixels.fill((0, 0, 0))
    for i in range(player_count):
        cp.pixels[i] = player_colors[i]


def start_timers(player_count):
    global turn_duration
    for player_index in range(player_count):
        start_turn(player_index, turn_duration)

def start_turn(player_index, duration):
    print(duration)
    cp.pixels.fill((0, 0, 0))  # Clear LEDs
    color = player_colors[player_index]  # Get the player's color
    end_time = time.monotonic() + duration
    leds_to_light = 10

    while time.monotonic() < end_time:
        # Update the displayed time
        current_time = time.monotonic()
        elapsed = current_time - (end_time - duration)
        leds_to_light = int((elapsed / duration) * 10)

        # Update LEDs to reflect remaining time
        for i in range(10):
            if i < 10 - leds_to_light:
                cp.pixels[i] = color
            else:
                cp.pixels[i] = (0, 0, 0)

        # Check for button press to end the turn early
        if cp.button_a or cp.button_b or cp.touch_A1:
            cp.pixels.fill((0, 255, 0))  # Indicate successful turn with green
            time.sleep(1)  # Short pause before next player's turn
            return

        time.sleep(0.1)  # Update interval

    # If the loop ends without a button press, player ran out of time
    print("Player", player_index + 1, "ran out of time!")
    cp.pixels.fill((255, 0, 0))  # Indicate timeout with red
    cp.play_tone(440, 1)  # Play a beep sound for 1 second
    time.sleep(1)

def update_duration_display():
    global turn_duration
    tens = turn_duration // 10
    ones = turn_duration % 10
    
    # Clear the LEDs before updating
    cp.pixels.fill((0, 0, 0))
    
    for i in range(10):
        if ones == 0:  # Special handling when ones digit is 0
            if i < tens:  # Set tens LEDs to blue
                color = (0, 0, 255)
            else:  # Remaining LEDs to green
                color = (0, 255, 0)
        else:
            color = (0, 0, 0)  # Default off
            if i < tens:  # Tens in blue
                color = (0, 0, 255)
            if i < ones:  # Ones in green
                color = (0, 255, 0)
            if i < tens and i < ones:  # Overlap in yellow
                color = (255, 255, 0)
        
        cp.pixels[i] = color

while True:
    if cp.switch:
        print("Starting Turns with", player_count, "players", turn_duration, "seconds")
        start_timers(player_count)
    else:
        if cp.shake(shake_threshold=20):
            print("Starting Hot Potato with", player_count, "players")
            hot_potato()
        # elif cp.loud_sound(sound_threshold=250):
        elif cp.touch_A6:
            print("Spin Wheel triggered by sound", cp.sound_level)
            spin_wheel()
        
        # Button A decreases player count
        if cp.button_a:
            player_count = max(2, player_count - 1)
            while cp.button_a:  # Wait for button release
                pass
            update_player_count()

        # Button B increases player count
        if cp.button_b:
            player_count = min(10, player_count + 1)
            while cp.button_b:  # Wait for button release
                pass
            update_player_count()

        if cp.touch_A3:
            turn_duration = min(99, turn_duration + 1)  # Adjust the maximum as needed
            while cp.touch_A4: pass
            update_duration_display()

        if cp.touch_A4:
            turn_duration = max(1, turn_duration - 1)
            while cp.touch_A3: pass
            update_duration_display()

