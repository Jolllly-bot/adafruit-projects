import pygame

def play_music(mp3_file, volume=1.0):
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_file)
    pygame.mixer.music.play()

    # Keep the music playing until it finishes
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

# Specify the path to your MP3 file
mp3_path = 'Flirting With June-Les Gordon.mp3'

# Call the function with the path to your MP3 file
play_music(mp3_path)
