"""Background music and sound-effect services."""
import pygame
from pathlib import Path


class AudioManager:
    def __init__(self):
        # Initialize mixer with optimized buffer to minimize audio latency
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self.sound_dir = Path("assets/sounds")
        self.sounds = {}

        # Default volume balance: keep BGM low so SFX are clearly audible
        self.music_volume = 0.25
        self.sound_volume = 1.0

        # Cooldown tracker to prevent overlapping sound spam (in milliseconds)
        self.last_played = {}
        self.sound_cooldowns = {
            "darkness": 400,  # Minimum 400ms between consecutive darkness triggers
            "build": 100
        }

    def load_sound(self, name, filename):
        """
        Load a sound effect from the sound directory.
        """
        path = self.sound_dir / filename
        if path.exists():
            sound = pygame.mixer.Sound(str(path))
            sound.set_volume(self.sound_volume)
            self.sounds[name] = sound
        else:
            print(f"[AudioManager] Warning: Sound file not found: {path}")

    def load_default_sounds(self):
        """
        Preload all required game sounds.
        """
        self.load_sound("button", "button_click.ogg")
        self.load_sound("build", "build.ogg")
        self.load_sound("bell", "bell.ogg")
        self.load_sound("darkness", "darkness.mp3")

    def play_sound(self, name):
        """
        Play a sound effect with anti-spam cooldown protection.
        """
        if name not in self.sounds:
            return

        current_time = pygame.time.get_ticks()
        cooldown = self.sound_cooldowns.get(name, 0)
        last_time = self.last_played.get(name, 0)

        # Only play if enough time has passed since last play
        if current_time - last_time >= cooldown:
            self.sounds[name].play()
            self.last_played[name] = current_time

    def play_music(self, filename="bgm.ogg", loop=True):
        """
        Play background music track.
        """
        path = self.sound_dir / filename
        if path.exists():
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1 if loop else 1)
        else:
            print(f"[AudioManager] Warning: Music file not found: {path}")

    def stop_music(self):
        """
        Stop currently playing background music.
        """
        pygame.mixer.music.stop()

    def set_music_volume(self, volume):
        """
        Update background music volume (0.0 to 1.0).
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def set_sound_volume(self, volume):
        """
        Update sound effect volume for all loaded sounds.
        """
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)