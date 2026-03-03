from __future__ import annotations

import array
import math
import random
from pathlib import Path

import pygame

# ---------------------------------------------------------------------------
# Sample-rate used for all synthesis (must match mixer init).
# ---------------------------------------------------------------------------
_SR = 44100


def _stereo(mono: array.array) -> bytes:
    """Interleave mono samples into stereo (L, R) and return raw bytes."""
    buf: array.array = array.array("h")
    for sample in mono:
        buf.append(sample)
        buf.append(sample)
    return buf.tobytes()


def _shoot() -> bytes:
    """Short descending chirp (classic laser zap)."""
    n = int(_SR * 0.12)
    mono: array.array = array.array("h")
    for i in range(n):
        t = i / _SR
        freq = 900 - 700 * (i / n)
        amp = int(14000 * (1 - i / n))
        mono.append(int(amp * math.sin(2 * math.pi * freq * t)))
    return _stereo(mono)


def _alien_hit() -> bytes:
    """Brief tonal burst that drops in pitch."""
    n = int(_SR * 0.14)
    mono: array.array = array.array("h")
    for i in range(n):
        t = i / _SR
        freq = 500 - 400 * (i / n)
        amp = int(12000 * (1 - i / n) ** 0.5)
        mono.append(int(amp * math.sin(2 * math.pi * freq * t)))
    return _stereo(mono)


def _player_hit() -> bytes:
    """Low rumbling explosion with noise."""
    n = int(_SR * 0.5)
    mono: array.array = array.array("h")
    rng = random.Random(42)
    for i in range(n):
        t = i / _SR
        tone = math.sin(2 * math.pi * 120 * t) + 0.5 * math.sin(2 * math.pi * 60 * t)
        noise = rng.uniform(-1, 1)
        raw = (tone * 0.6 + noise * 0.4) * 18000 * (1 - i / n) ** 0.7
        mono.append(max(-32767, min(32767, int(raw))))
    return _stereo(mono)


def _ufo() -> bytes:
    """Warbling two-tone drone (loops automatically)."""
    n = int(_SR * 0.48)
    mono: array.array = array.array("h")
    for i in range(n):
        t = i / _SR
        lfo = 0.5 + 0.5 * math.sin(2 * math.pi * 4 * t)
        freq = 120 + 80 * lfo
        raw = 10000 * math.sin(2 * math.pi * freq * t)
        mono.append(int(raw))
    return _stereo(mono)


def _ufo_hit() -> bytes:
    """Descending explosion with harmonic crunch."""
    n = int(_SR * 0.35)
    mono: array.array = array.array("h")
    rng = random.Random(7)
    for i in range(n):
        t = i / _SR
        freq = 800 * (1 - i / n) ** 2 + 40
        tone = math.sin(2 * math.pi * freq * t)
        noise = rng.uniform(-1, 1) * 0.3
        amp = 20000 * (1 - i / n) ** 0.5
        mono.append(max(-32767, min(32767, int(amp * (tone + noise)))))
    return _stereo(mono)


# Four alternating bass thumps that cycle on every alien step, recreating the
# original arcade "dun-dun-dun-dun" heartbeat.  Pitches match the arcade PCB
# frequencies as closely as practical with a simple sine + quick decay.
_MARCH_FREQS = [160, 120, 100, 80]  # Hz, one per beat in the cycle


def _march_note(freq: int) -> bytes:
    n = int(_SR * 0.09)          # 90 ms per thump
    mono: array.array = array.array("h")
    for i in range(n):
        t = i / _SR
        # Sine fundamental + one octave up for body, fast exponential decay
        tone = (
            math.sin(2 * math.pi * freq * t)
            + 0.4 * math.sin(2 * math.pi * freq * 2 * t)
        )
        amp = int(26000 * math.exp(-18 * t))
        mono.append(max(-32767, min(32767, int(amp * tone))))
    return _stereo(mono)


# ---------------------------------------------------------------------------
# SoundSystem
# ---------------------------------------------------------------------------

_SYNTH: dict[str, bytes] = {}


def _get_synth(key: str) -> bytes:
    """Lazily generate and cache synthesised sounds."""
    if key not in _SYNTH:
        _SYNTH[key] = {
            "shoot": _shoot,
            "alien_hit": _alien_hit,
            "player_hit": _player_hit,
            "ufo": _ufo,
            "ufo_hit": _ufo_hit,
        }[key]()
    return _SYNTH[key]


class SoundSystem:
    def __init__(self, audio_dir: Path) -> None:
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._march_sounds: list[pygame.mixer.Sound] = []
        self._march_beat: int = 0

        try:
            available = pygame.mixer.get_init()
        except (NotImplementedError, AttributeError):
            return
        if not available:
            return

        for key in ("shoot", "alien_hit", "player_hit", "ufo", "ufo_hit"):
            path = audio_dir / f"{key}.wav"
            if path.exists():
                # Prefer a supplied file.
                self._sounds[key] = pygame.mixer.Sound(path.as_posix())
            else:
                # Fall back to a synthesised sound.
                self._sounds[key] = pygame.mixer.Sound(buffer=_get_synth(key))

        # UFO sound loops until the UFO leaves the screen.
        if "ufo" in self._sounds:
            self._sounds["ufo"].set_volume(0.55)

        # Pre-build the 4 cycling march notes.
        for freq in _MARCH_FREQS:
            self._march_sounds.append(
                pygame.mixer.Sound(buffer=_march_note(freq))
            )

    def play(self, key: str, loop: bool = False) -> None:
        sound = self._sounds.get(key)
        if sound is not None:
            sound.play(loops=-1 if loop else 0)

    def stop(self, key: str) -> None:
        sound = self._sounds.get(key)
        if sound is not None:
            sound.stop()

    def play_march(self) -> None:
        """Play the next note in the 4-beat alien march cycle."""
        if not self._march_sounds:
            return
        self._march_sounds[self._march_beat % 4].play()
        self._march_beat += 1

    def reset_march(self) -> None:
        """Reset the beat counter (call on wave reset / new game)."""
        self._march_beat = 0
