from __future__ import annotations

import pygame


class Bullet:
    """A projectile fired upward by the player.

    Attributes
    ----------
    x, y        Top-left position (floats for sub-pixel precision).
    width       Sprite width in pixels.
    height      Sprite height in pixels.
    speed       Travel speed in pixels per second.
    direction   Always -1 (upward).
    """

    WIDTH = 4
    HEIGHT = 14
    SPEED = 420.0
    DIRECTION = -1  # upward

    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y
        self.width: int = self.WIDTH
        self.height: int = self.HEIGHT
        self.speed: float = self.SPEED
        self.direction: int = self.DIRECTION

    def update(self, dt: float) -> None:
        self.y += self.direction * self.speed * dt

    @property
    def is_off_screen(self) -> bool:
        return self.y + self.height < 0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (240, 240, 240), self.rect)
        # Bright tip for a classic arcade look
        pygame.draw.rect(
            surface,
            (255, 255, 180),
            pygame.Rect(int(self.x), int(self.y), self.width, 3),
        )
