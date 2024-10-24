import time
from adafruit_circuitplayground import cp
import math
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

ble = BLERadio()
ble.name = "J's Circuit Playground"
uart_server = UARTService()
advertisement = ProvideServicesAdvertisement(uart_server)


def calculate_magnitude(x, y, z):
    """Calculate the magnitude of the acceleration vector."""
    return (x**2 + y**2 + z**2)**0.5


# Initialize variables
alpha = 0.1  # Smoothing factor for EMA
ema_magnitude = 0
last_ema_magnitude = calculate_magnitude(*cp.acceleration) - 9.81
change_in_magnitude = 0
# Define thresholds for motion and braking detection
motion_threshold = 0.2  # Adjust based on sensitivity required for motion
braking_threshold = -1.0  # Adjust based on testing for deceleration sensitivity

brightness = 0
brightness_direction = 0.05  # Controls the rate of breathing effect
bpm = 0


def update_light_breathing():
    global brightness, brightness_direction
    cp.pixels.brightness = abs(math.sin(brightness)) * 0.5  # Adjust the max brightness with the multiplier
    brightness += brightness_direction
    if brightness >= math.pi * 2:  # Reset brightness to keep it in the sin wave cycle
        brightness = 0
    cp.pixels.fill((255, 165, 0))


def update_light_moving():
    cp.pixels.fill((0, 0, 0))  # Turn off LEDs


def update_light_braking():
    cp.pixels.fill((255, 0, 0))  # Turn on LEDs (red) for braking


NUM_OVERSAMPLE = 10
NUM_SAMPLES = 20


def measure_heart_rate():
    cp.pixels.brightness = 1.0
    samples = [0] * NUM_SAMPLES
    pulse_count = 0
    start_time = time.monotonic()

    while cp.button_a:  # Measure while the button is pressed
        cp.pixels[0] = (0, 255, 0)  # LED's 0 and 1 shine into your finger
        cp.pixels[1] = (0, 255, 0)
        for i in range(NUM_SAMPLES):
            oversample = 0
            for s in range(NUM_OVERSAMPLE):
                oversample += float(cp.light)
            samples[i] = oversample / NUM_OVERSAMPLE
            mean = sum(samples) / len(samples)
            # print((samples[i],cp.light))

            # Pulse detection logic
            if i > 0:
                if (samples[i]-mean) <= 0 and (samples[i-1]-mean) > 0:
                    cp.pixels[9] = (20, 0, 0)  # Show pulse detection
                    pulse_count += 1
                else:
                    cp.pixels[9] = (0, 0, 0)
                time.sleep(0.025)

    # Calculate BPM
    elapsed_time = time.monotonic() - start_time
    bpm = (pulse_count / (elapsed_time / 60))
    print("Heart Rate: ", bpm, "BPM")
    return bpm


def display_heart_rate(bpm):
    cp.pixels.fill((0, 0, 0))  # Turn off all LEDs before displaying heart rate
    num_leds_to_light = max(0, min(int(bpm) // 10, 10))
    print(num_leds_to_light)
    for i in range(num_leds_to_light):
        cp.pixels[i] = (0, 0, 255)  # Use blue LEDs for display


def emergency_mode():
    """Activate emergency mode if A and B pressed for 1 min."""

    cp.pixels.fill((255, 0, 0))
    cp.play_tone(440, 0.5)
    cp.red_led = False
    cp.play_tone(880, 0.5)


def send_data_over_ble(ema_magnitude, change, heart_rate, temp):
    """Send data over BLE with timestamp."""
    if ble.connected:
        timestamp = time.monotonic()  # Simple timestamp, replace or augment with real-time if needed
        data = f"{ema_magnitude}, {change}, {heart_rate}, {temp}\n"
        uart_server.write(data.encode())


emergency = False
DANGER_TEMP = -15

# BLUETOOTH
ble.start_advertising(advertisement)
while not ble.connected:
    pass
ble.stop_advertising()
print("Connected!")

while True:

    temp = cp.temperature

    if temp < DANGER_TEMP:
        print("Temperature below threshold, activating emergency mode")
        emergency = True

    if cp.button_a and cp.button_b:
        print("Emergency mode toggle")
        start_time_em = time.monotonic()
        while cp.button_a and cp.button_b:
            print(time.monotonic() - start_time_em)
            if time.monotonic() - start_time_em >= 1:
                emergency = not emergency
                break

    if emergency:
        print("Emergency mode ON")
        emergency_mode()

    else:
        # print("Emergency mode OFF")
        if (cp.switch):
            update_light_moving()
            x, y, z = cp.acceleration
            current_magnitude = calculate_magnitude(x, y, z) - 9.81  # Adjusting for gravity

            # Update EMA of the acceleration magnitude
            ema_magnitude = alpha * current_magnitude + (1 - alpha) * last_ema_magnitude
            change_in_magnitude = ema_magnitude - last_ema_magnitude

            if cp.button_a:
                braking_threshold -= 0.1
                print("braking thre:", braking_threshold)
            if cp.button_b:
                braking_threshold += 0.1
                print("braking thre:", braking_threshold)

            print(change_in_magnitude)

            if abs(change_in_magnitude) < motion_threshold:
                # The device is relatively stationary or moving very little
                update_light_breathing()
            elif change_in_magnitude < braking_threshold:
                # Significant deceleration detected
                update_light_braking()
                cp.start_tone(1000)
                time.sleep(0.5)
                cp.stop_tone()
            else:
                # The device is in motion, not significantly decelerating
                update_light_moving()

            last_ema_magnitude = ema_magnitude  # Update the last EMA magnitude for the next iteration
            time.sleep(0.1)
        else:
            if cp.button_a:  # Wait for button press to start measurement
                cp.pixels.fill((0, 0, 0))
                bpm = measure_heart_rate()  # Measure heart rate while button is pressed
                display_heart_rate(bpm)  # Display the heart rate after button is released
                while cp.button_a:  # Optional: wait for button release before allowing another measurement
                    pass  # Do nothing, just wait

        # BLUETOOTH
        send_data_over_ble(ema_magnitude, change_in_magnitude, bpm, temp)
