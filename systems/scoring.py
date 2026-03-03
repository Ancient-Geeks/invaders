from __future__ import annotations


class ScoreSystem:
    # Shot-counter lookup table for UFO mystery values (original arcade sequence).
    _UFO_TABLE = [100, 50, 50, 100, 150, 100, 100, 50, 300, 100, 50, 100, 150, 100, 50]

    def __init__(self) -> None:
        self.value: int = 0
        self.high_score: int = 0
        self._shot_counter: int = 0

    def add_alien(self, points: int) -> None:
        self.value += points
        self.high_score = max(self.high_score, self.value)

    def register_player_shot(self) -> None:
        self._shot_counter += 1

    def ufo_value(self) -> int:
        return self._UFO_TABLE[self._shot_counter % len(self._UFO_TABLE)]

    def add_ufo(self) -> int:
        points = self.ufo_value()
        self.value += points
        self.high_score = max(self.high_score, self.value)
        return points
