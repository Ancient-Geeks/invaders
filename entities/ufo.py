from __future__ import annotations

import pygame


class Ufo:
    """The mystery-score UFO that traverses the top of the screen."""

    WIDTH = 52
    HEIGHT = 24

    SPEED = 80

    def __init__(self) -> None:
        self.active: bool = False
        self._vx: int = self.SPEED
        self.rect = pygame.Rect(-self.WIDTH, 44, self.WIDTH, self.HEIGHT)

    def spawn(self, *, from_left: bool) -> None:
        self.active = True
        if from_left:
            self.rect.x = -self.WIDTH
            self._vx = self.SPEED
        else:
            self.rect.x = 800 + self.WIDTH
            self._vx = -self.SPEED

    def update(self, dt: float) -> None:
        if not self.active:
            return
        self.rect.x += int(self._vx * dt)
        if self.rect.right < -20 or self.rect.left > 820:
            self.active = False

    def draw(self, surface: pygame.Surface, frame_toggle: bool) -> None:
        if not self.active:
            return
        pygame.draw.ellipse(surface, (255, 60, 60), self.rect)
        cockpit = pygame.Rect(
            self.rect.x + 14,
            self.rect.y + (5 if frame_toggle else 7),
            24,
            8,
        )
        pygame.draw.rect(surface, (255, 180, 180), cockpit)
