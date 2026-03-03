from __future__ import annotations

from collections.abc import Sequence

import pygame

from entities.alien import Alien
from entities.projectile import Projectile
from entities.shield import Shield
from entities.ufo import Ufo


def _sample_points(rect: pygame.Rect) -> list[tuple[int, int]]:
    cx = rect.centerx
    return [(cx, rect.top), (cx, rect.centery), (cx, rect.bottom - 1)]


def handle_shield_collisions(
    projectile: Projectile,
    shields: Sequence[Shield],
) -> bool:
    pts = _sample_points(projectile.rect)
    for shield in shields:
        if shield.intersects_points(pts):
            impact = pts[-1] if projectile.from_player else pts[0]
            shield.damage(impact, radius=5)
            return True
    return False


def handle_alien_hit(
    projectile: Projectile,
    aliens: Sequence[Alien],
) -> Alien | None:
    for alien in aliens:
        if alien.alive and projectile.rect.colliderect(alien.rect):
            alien.alive = False
            return alien
    return None


def handle_ufo_hit(projectile: Projectile, ufo: Ufo) -> bool:
    if ufo.active and projectile.rect.colliderect(ufo.rect):
        ufo.active = False
        return True
    return False
