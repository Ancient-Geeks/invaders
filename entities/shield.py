from __future__ import annotations

import random
from collections.abc import Iterable

import pygame


# Pixel template for one shield (20 cols × 12 rows); '#' = solid, '.' = transparent
_TEMPLATE = [
    "....................",
    ".....##########.....",
    "...##############...",
    "..################..",
    ".##################.",
    ".##################.",
    "####################",
    "####################",
    "####################",
    "########....########",
    "#######......#######",
    "######........######",
]


class Shield:
    def __init__(self, left: int, top: int, scale: int = 3) -> None:
        self.scale = scale
        self.surface = self._build_surface()
        self.rect = self.surface.get_rect(topleft=(left, top))

    def _build_surface(self) -> pygame.Surface:
        cols = len(_TEMPLATE[0])
        rows = len(_TEMPLATE)
        surface = pygame.Surface((cols * self.scale, rows * self.scale), pygame.SRCALPHA)
        for row_i, row in enumerate(_TEMPLATE):
            for col_i, ch in enumerate(row):
                if ch == "#":
                    block = pygame.Rect(
                        col_i * self.scale,
                        row_i * self.scale,
                        self.scale,
                        self.scale,
                    )
                    pygame.draw.rect(surface, (60, 220, 90, 255), block)
        return surface

    # ------------------------------------------------------------------
    # Erosion
    # ------------------------------------------------------------------

    def damage(self, world_point: tuple[int, int], radius: int = 6) -> None:
        lx = world_point[0] - self.rect.x
        ly = world_point[1] - self.rect.y
        for _ in range(8):
            ox = random.randint(-3, 3)
            oy = random.randint(-3, 3)
            r = max(2, radius + random.randint(-1, 3))
            pygame.draw.circle(self.surface, (0, 0, 0, 0), (lx + ox, ly + oy), r)

    def alpha_at(self, world_point: tuple[int, int]) -> int:
        lx = world_point[0] - self.rect.x
        ly = world_point[1] - self.rect.y
        w, h = self.surface.get_size()
        if not (0 <= lx < w and 0 <= ly < h):
            return 0
        return self.surface.get_at((lx, ly)).a

    def intersects_points(self, points: Iterable[tuple[int, int]]) -> bool:
        return any(self.alpha_at(p) > 0 for p in points)

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, self.rect)
