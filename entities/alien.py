from __future__ import annotations

from dataclasses import dataclass, field

import pygame


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

        # Body
        pygame.draw.rect(surface, (160, 255, 80), self.rect, border_radius=2)

        # Animated eyes
        eye_y = self.rect.y + (4 if frame_toggle else 3)
        pygame.draw.circle(surface, (0, 0, 0), (self.rect.x + 8, eye_y), 2)
        pygame.draw.circle(surface, (0, 0, 0), (self.rect.x + self.rect.width - 8, eye_y), 2)

        # Animated legs
        leg_y = self.rect.bottom - (2 if frame_toggle else 4)
        for lx in (self.rect.x + 4, self.rect.x + self.rect.width - 4):
            pygame.draw.line(surface, (160, 255, 80), (lx, self.rect.bottom), (lx, leg_y), 2)
