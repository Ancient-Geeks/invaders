from __future__ import annotations

from dataclasses import dataclass, field

import pygame


@dataclass(slots=True)
class Projectile:
    rect: pygame.Rect
    velocity_y: float
    from_player: bool

    def update(self, dt: float) -> None:
        self.rect.y += int(self.velocity_y * dt)

    @property
    def alive(self) -> bool:
        return -20 <= self.rect.y <= 700

    def draw(self, surface: pygame.Surface) -> None:
        color = (240, 240, 240) if self.from_player else (255, 90, 90)
        pygame.draw.rect(surface, color, self.rect)
