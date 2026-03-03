from __future__ import annotations

import pygame


class Player:
    """The player's cannon ship.

    Attributes
    ----------
    x, y        Top-left position (floats for sub-pixel precision).
    width       Sprite width in pixels.
    height      Sprite height in pixels.
    speed       Horizontal movement speed in pixels per second.
    lives       Remaining lives.
    """

    WIDTH = 42
    HEIGHT = 24

    def __init__(self, x: float, y: float, screen_width: int) -> None:
        self.x: float = x
        self.y: float = y
        self.width: int = self.WIDTH
        self.height: int = self.HEIGHT
        self.speed: float = 260.0
        self.lives: int = 3

        self._screen_width = screen_width
        self._dx: float = 0.0
        self._respawn_timer: float = 0.0
        self.visible: bool = True

    # ------------------------------------------------------------------
    # Movement API
    # ------------------------------------------------------------------

    def move_left(self) -> None:
        self._dx = -1.0

    def move_right(self) -> None:
        self._dx = 1.0

    def update(self, dt: float) -> None:
        if self._respawn_timer > 0.0:
            self._respawn_timer = max(0.0, self._respawn_timer - dt)
            self.visible = self._respawn_timer == 0.0
            return

        self.x += self._dx * self.speed * dt
        self.x = max(0.0, min(float(self._screen_width - self.width), self.x))
        self._dx = 0.0

    # ------------------------------------------------------------------
    # Combat
    # ------------------------------------------------------------------

    def can_fire(self) -> bool:
        return self.visible and self._respawn_timer == 0.0

    def hit(self) -> None:
        self.lives -= 1
        self._respawn_timer = 1.8
        self.visible = False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        ix, iy = int(self.x), int(self.y)
        body       = pygame.Rect(ix + 8,  iy + 8,  26, 12)
        cannon     = pygame.Rect(ix + 18, iy,       6,  10)
        wing_left  = pygame.Rect(ix,      iy + 12, 12,   8)
        wing_right = pygame.Rect(ix + 30, iy + 12, 12,   8)

        for part in (body, cannon, wing_left, wing_right):
            pygame.draw.rect(surface, (80, 255, 80), part)
