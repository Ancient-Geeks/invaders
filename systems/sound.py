from __future__ import annotations

from pathlib import Path

import pygame


class SoundSystem:
    def __init__(self, audio_dir: Path) -> None:
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            available = pygame.mixer.get_init()
        except (NotImplementedError, AttributeError):
            return
        if not available:
            return
        for key in ("shoot", "alien_hit", "player_hit", "ufo", "ufo_hit"):
            path = audio_dir / f"{key}.wav"
            if path.exists():
                self._sounds[key] = pygame.mixer.Sound(path.as_posix())

    def play(self, key: str) -> None:
        sound = self._sounds.get(key)
        if sound is not None:
            sound.play()
