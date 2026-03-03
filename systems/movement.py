from __future__ import annotations

from collections.abc import Sequence

from entities.alien import Alien


def alien_step_interval(alive_count: int) -> float:
    """Return seconds between alien march steps.

    At 55 aliens the cadence is slow (0.60 s); at 1 alien it hits 0.08 s,
    mirroring the original hardware behaviour where remaining ROM cycles
    drove update speed.
    """
    progress = max(0.0, min(1.0, (55 - alive_count) / 54.0))
    return 0.60 - progress * 0.52


def max_alien_bullets(alive_count: int) -> int:
    if alive_count > 36:
        return 1
    if alive_count > 16:
        return 2
    return 3


def move_formation(
    aliens: Sequence[Alien],
    direction: int,
    horizontal_step: int,
    descend_step: int,
) -> tuple[int, bool]:
    """Move the alien formation one step and return (new_direction, descended)."""
    alive = [a for a in aliens if a.alive]
    if not alive:
        return direction, False

    min_x = min(a.rect.left for a in alive)
    max_x = max(a.rect.right for a in alive)

    hit_edge = (direction > 0 and max_x + horizontal_step >= 784) or (
        direction < 0 and min_x - horizontal_step <= 16
    )

    if hit_edge:
        for a in alive:
            a.rect.y += descend_step
        return -direction, True

    for a in alive:
        a.rect.x += direction * horizontal_step
    return direction, False
