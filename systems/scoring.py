from __future__ import annotations

import json
from pathlib import Path

# Saved next to this file's package root (i.e. the project directory).
_SAVE_FILE = Path(__file__).parent.parent / "hiscore.json"


class ScoreSystem:
    # Shot-counter lookup table for UFO mystery values (original arcade sequence).
    _UFO_TABLE = [100, 50, 50, 100, 150, 100, 100, 50, 300, 100, 50, 100, 150, 100, 50]

    def __init__(self) -> None:
        self.value: int = 0
        self.high_score: int = _load_hiscore()
        self._shot_counter: int = 0

    def _try_save(self) -> None:
        if self.value >= self.high_score:
            self.high_score = self.value
            _save_hiscore(self.high_score)

    def add_alien(self, points: int) -> None:
        self.value += points
        self._try_save()

    def register_player_shot(self) -> None:
        self._shot_counter += 1

    def ufo_value(self) -> int:
        return self._UFO_TABLE[self._shot_counter % len(self._UFO_TABLE)]

    def add_ufo(self) -> int:
        points = self.ufo_value()
        self.value += points
        self._try_save()
        return points


def _load_hiscore() -> int:
    try:
        return int(json.loads(_SAVE_FILE.read_text())["hiscore"])
    except Exception:
        return 0


def _save_hiscore(value: int) -> None:
    try:
        _SAVE_FILE.write_text(json.dumps({"hiscore": value}))
    except Exception:
        pass
