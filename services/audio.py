"""Background music and sound-effect services."""
import pygame
from pathlib import Path


class AudioManager:
    def __init__(self):
        self.sound_dir = Path("assets/sounds")

        self.sounds = {}

        self.music_volume = 0.5
        self.sound_volume = 0.7

    def load_sound(self, name, filename):
        path = self.sound_dir / filename
        self.sounds[name] = pygame.mixer.Sound(path)
        self.sounds[name].set_volume(self.sound_volume)

    def load_default_sounds(self):
        self.load_sound("button", "button_click.ogg")
        self.load_sound("build", "build.ogg")
        self.load_sound("bell", "bell.ogg")
        self.load_sound("darkness", "darkness.mp3")

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def play_music(self, filename, loop=True):
        path = self.sound_dir / filename

        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(self.music_volume)

        if loop:
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.play()

    def stop_music(self):
        pygame.mixer.music.stop()

    def set_music_volume(self, volume):
        self.music_volume = volume
        pygame.mixer.music.set_volume(volume)

    def set_sound_volume(self, volume):
        self.sound_volume = volume

        for sound in self.sounds.values():
            sound.set_volume(volume)