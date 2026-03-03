from __future__ import annotations

from dataclasses import dataclass, field

import pygame

# ---------------------------------------------------------------------------
# Pixel-art sprite data  (11 cols × 8 rows, '1' = filled, '.' = transparent)
# Two entries per list: [frame_A, frame_B]
# ---------------------------------------------------------------------------

# Row 0 — Squid (30 pts): narrow, antennae, beak-mouth
_SQUID: list[list[str]] = [
    [   # frame A
        "....11.....",
        "...1111....",
        ".11111111..",
        "11.11.11.11",
        "11111111111",
        ".11.....11.",   # ← mouth gap in centre
        "..1.1.1.1..",
        ".1.......1.",
    ],
    [   # frame B
        "....11.....",
        "...1111....",
        ".11111111..",
        "11.11.11.11",
        "11111111111",
        ".11.....11.",   # ← same mouth
        "...1...1...",
        "1.1.....1.1",
    ],
]

# Rows 1-2 — Crab (20 pts): wide arms that alternate, toothed mouth
_CRAB: list[list[str]] = [
    [   # frame A — arms spread out wide
        "1.........1",
        ".1.......1.",
        ".1.11111.1.",
        ".11.111.11.",
        "11111111111",
        ".11.....11.",   # ← mouth gap
        "1.1.....1.1",
        "...1...1...",
    ],
    [   # frame B — arms tucked in
        ".1.......1.",
        "1..1...1..1",
        ".1.11111.1.",
        ".11.111.11.",
        "11111111111",
        ".11.....11.",   # ← same mouth
        "..1.....1..",
        ".1.......1.",
    ],
]

# Rows 3-4 — Octopus (10 pts): round dome, wide-open mouth, legs alternate
_OCTOPUS: list[list[str]] = [
    [   # frame A
        "...11111...",
        ".111111111.",
        "11111111111",
        "11.11111.11",
        "11111111111",
        "..11...11..",   # ← wide open mouth — gap in centre
        ".1.1.1.1.1.",
        "1.1.....1.1",
    ],
    [   # frame B
        "...11111...",
        ".111111111.",
        "11111111111",
        "11.11111.11",
        "11111111111",
        "..11...11..",   # ← same mouth
        ".11.1.1.11.",
        "1...1.1...1",
    ],
]

# Colour per score tier (evokes the original coloured-overlay look)
_COLORS = {
    0: (255, 210, 80),   # squid   — yellow
    1: (80,  210, 255),  # crab    — cyan
    2: (80,  210, 255),
    3: (160, 255, 80),   # octopus — green
    4: (160, 255, 80),
}


def _draw_sprite(
    surface: pygame.Surface,
    rect: pygame.Rect,
    frames: list[list[str]],
    frame_toggle: bool,
    color: tuple[int, int, int],
) -> None:
    sprite = frames[1 if frame_toggle else 0]
    rows = len(sprite)
    cols = len(sprite[0])
    pw = rect.width / cols
    ph = rect.height / rows
    for ry, row in enumerate(sprite):
        for cx, ch in enumerate(row):
            if ch == "1":
                pygame.draw.rect(
                    surface,
                    color,
                    pygame.Rect(
                        rect.x + round(cx * pw),
                        rect.y + round(ry * ph),
                        max(1, round(pw)),
                        max(1, round(ph)),
                    ),
                )


@dataclass(slots=True)
class Alien:
    rect: pygame.Rect
    row: int
    col: int
    alive: bool = field(default=True)

    @property
    def score_value(self) -> int:
        if self.row == 0:
            return 30
        if self.row in (1, 2):
            return 20
        return 10

    def draw(self, surface: pygame.Surface, frame_toggle: bool) -> None:
        if not self.alive:
            return

        if self.row == 0:
            frames = _SQUID
        elif self.row <= 2:
            frames = _CRAB
        else:
            frames = _OCTOPUS

        _draw_sprite(surface, self.rect, frames, frame_toggle, _COLORS[self.row])
