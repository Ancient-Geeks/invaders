from __future__ import annotations

import random
from pathlib import Path
from typing import Optional

import pygame

from entities.alien import Alien
from entities.bullet import Bullet
from entities.player import Player
from entities.projectile import Projectile
from entities.shield import Shield
from entities.ufo import Ufo
from systems.collisions import handle_alien_hit, handle_shield_collisions, handle_ufo_hit
from systems.movement import alien_step_interval, max_alien_bullets, move_formation
from systems.scoring import ScoreSystem
from systems.sound import SoundSystem

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
FIXED_DT = 1.0 / FPS

ALIEN_ROWS = 5
ALIEN_COLS = 11
FIRE_COOLDOWN = 0.25  # minimum seconds between player shots


# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------

class Game:
    def __init__(self) -> None:
        pygame.init()
        try:
            pygame.mixer.init()
        except (pygame.error, NotImplementedError, AttributeError):
            pass

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Courier New", 22)
        self.small_font = pygame.font.SysFont("Courier New", 18)

        self.sound = SoundSystem(Path("assets") / "audio")
        self.score = ScoreSystem()

        self.wave: int = 1
        self.game_over: bool = False

        # Alien march state
        self.alien_direction: int = 1
        self.alien_move_timer: float = 0.0
        self.alien_fire_timer: float = 0.0
        self.frame_toggle: bool = False
        self.anim_timer: float = 0.0

        # UFO
        self.ufo = Ufo()
        self.ufo_spawn_timer: float = random.uniform(10.0, 18.0)
        self.ufo_popup: Optional[tuple[int, float, float, int]] = None  # (x, y, ttl, pts)

        # Player
        self.player = Player(
            x=SCREEN_WIDTH / 2 - Player.WIDTH / 2,
            y=SCREEN_HEIGHT - 56,
            screen_width=SCREEN_WIDTH,
        )
        self.fire_cooldown: float = 0.0
        self.bullet: Optional[Bullet] = None

        # Alien projectiles (multiple allowed; player uses single Bullet above)
        self.alien_projectiles: list[Projectile] = []

        self.aliens = self._make_formation()
        self.shields = self._make_shields()

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------

    def _make_formation(self) -> list[Alien]:
        aliens: list[Alien] = []
        for row in range(ALIEN_ROWS):
            for col in range(ALIEN_COLS):
                rect = pygame.Rect(110 + col * 48, 110 + row * 36, 30, 22)
                aliens.append(Alien(rect=rect, row=row, col=col))
        return aliens

    def _make_shields(self) -> list[Shield]:
        return [Shield(left, 430) for left in (100, 260, 420, 580)]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _alive_aliens(self) -> list[Alien]:
        return [a for a in self.aliens if a.alive]

    def _reset_wave(self) -> None:
        self.wave += 1
        self.aliens = self._make_formation()
        self.shields = self._make_shields()
        self.alien_direction = 1
        self.alien_move_timer = 0.0
        self.alien_fire_timer = 0.0
        self.bullet = None
        self.alien_projectiles.clear()
        self.ufo.active = False

    # ------------------------------------------------------------------
    # Update sub-systems
    # ------------------------------------------------------------------

    def _update_player_input(self, dt: float) -> None:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.player.move_left()
        if keys[pygame.K_RIGHT]:
            self.player.move_right()

        self.player.update(dt)

        self.fire_cooldown = max(0.0, self.fire_cooldown - dt)

        if (
            keys[pygame.K_SPACE]
            and self.bullet is None
            and self.fire_cooldown == 0.0
            and self.player.can_fire()
        ):
            self.bullet = Bullet(
                x=self.player.x + self.player.width / 2 - Bullet.WIDTH / 2,
                y=self.player.y - Bullet.HEIGHT,
            )
            self.fire_cooldown = FIRE_COOLDOWN
            self.score.register_player_shot()
            self.sound.play("shoot")

    def _update_alien_march(self, dt: float) -> None:
        alive = self._alive_aliens()
        if not alive:
            self._reset_wave()
            return

        # Animate regardless of march timer
        self.anim_timer += dt
        if self.anim_timer >= 0.25:
            self.anim_timer = 0.0
            self.frame_toggle = not self.frame_toggle

        self.alien_move_timer += dt
        if self.alien_move_timer < alien_step_interval(len(alive)):
            return
        self.alien_move_timer = 0.0

        self.alien_direction, _ = move_formation(
            alive,
            direction=self.alien_direction,
            horizontal_step=10,
            descend_step=18,
        )

        # Invasion — aliens have reached the player's row
        if max(a.rect.bottom for a in alive) >= self.player.rect.top:
            self.game_over = True

    def _update_alien_fire(self, dt: float) -> None:
        alive = self._alive_aliens()
        if not alive:
            return

        allowed = max_alien_bullets(len(alive))
        self.alien_fire_timer += dt
        interval = 0.80 if len(alive) > 20 else 0.55

        if (
            self.alien_fire_timer >= interval
            and len(self.alien_projectiles) < allowed
        ):
            self.alien_fire_timer = 0.0

            # Only the bottom-most alien in a column can fire.
            col_bottom: dict[int, Alien] = {}
            for a in alive:
                if a.col not in col_bottom or a.rect.y > col_bottom[a.col].rect.y:
                    col_bottom[a.col] = a
            shooter = random.choice(list(col_bottom.values()))
            self.alien_projectiles.append(
                Projectile(
                    rect=pygame.Rect(shooter.rect.centerx - 2, shooter.rect.bottom + 2, 4, 14),
                    velocity_y=260.0,
                    from_player=False,
                )
            )

    def _update_ufo(self, dt: float) -> None:
        if self.ufo.active:
            self.ufo.update(dt)
        else:
            self.ufo_spawn_timer -= dt
            if self.ufo_spawn_timer <= 0.0:
                self.ufo.spawn(from_left=random.choice([True, False]))
                self.ufo_spawn_timer = random.uniform(12.0, 20.0)
                self.sound.play("ufo")

        if self.ufo_popup is not None:
            x, y, ttl, pts = self.ufo_popup
            ttl -= dt
            self.ufo_popup = (x, y - 18.0 * dt, ttl, pts) if ttl > 0.0 else None

    def _update_projectiles(self, dt: float) -> None:
        # --- player bullet ---
        if self.bullet is not None:
            self.bullet.update(dt)
            if self.bullet.is_off_screen:
                self.bullet = None
            else:
                # vs shields
                b_rect = self.bullet.rect
                shot_as_projectile = Projectile(rect=b_rect, velocity_y=0, from_player=True)
                if handle_shield_collisions(shot_as_projectile, self.shields):
                    self.bullet = None
                elif (alien := handle_alien_hit(shot_as_projectile, self.aliens)) is not None:
                    self.score.add_alien(alien.score_value)
                    self.sound.play("alien_hit")
                    self.bullet = None
                elif handle_ufo_hit(shot_as_projectile, self.ufo):
                    pts = self.score.add_ufo()
                    self.ufo_popup = (self.ufo.rect.centerx, float(self.ufo.rect.y), 1.0, pts)
                    self.sound.play("ufo_hit")
                    self.bullet = None

        # --- alien projectiles ---
        for proj in self.alien_projectiles:
            proj.update(dt)
        self.alien_projectiles = [p for p in self.alien_projectiles if p.alive]

        surviving: list[Projectile] = []
        for proj in self.alien_projectiles:
            if handle_shield_collisions(proj, self.shields):
                continue
            # Cancel against player bullet
            if self.bullet is not None and proj.rect.colliderect(self.bullet.rect):
                self.bullet = None
                continue
            if self.player.can_fire() and proj.rect.colliderect(self.player.rect):
                self.player.hit()
                self.sound.play("player_hit")
                if self.player.lives <= 0:
                    self.game_over = True
                continue
            surviving.append(proj)
        self.alien_projectiles = surviving

    # ------------------------------------------------------------------
    # Public update / draw
    # ------------------------------------------------------------------

    def update(self, dt: float) -> None:
        if self.game_over:
            return
        self._update_player_input(dt)
        self._update_alien_march(dt)
        self._update_alien_fire(dt)
        self._update_ufo(dt)
        self._update_projectiles(dt)

    def draw(self) -> None:
        self.screen.fill((6, 6, 12))

        # Ground line
        pygame.draw.line(
            self.screen, (70, 160, 70),
            (0, SCREEN_HEIGHT - 40), (SCREEN_WIDTH, SCREEN_HEIGHT - 40), 2,
        )

        for shield in self.shields:
            shield.draw(self.screen)

        for alien in self.aliens:
            alien.draw(self.screen, self.frame_toggle)

        self.ufo.draw(self.screen, self.frame_toggle)

        if self.bullet is not None:
            self.bullet.draw(self.screen)

        for proj in self.alien_projectiles:
            proj.draw(self.screen)

        self.player.draw(self.screen)

        # UFO score popup
        if self.ufo_popup is not None:
            x, y, _, pts = self.ufo_popup
            surf = self.small_font.render(str(pts), True, (255, 180, 180))
            self.screen.blit(surf, (x - surf.get_width() // 2, int(y)))

        self._draw_hud()

        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_hud(self) -> None:
        self.screen.blit(
            self.font.render(f"SCORE  {self.score.value:05d}", True, (240, 240, 240)),
            (18, 10),
        )
        self.screen.blit(
            self.font.render(f"HI  {self.score.high_score:05d}", True, (240, 240, 240)),
            (SCREEN_WIDTH // 2 - 70, 10),
        )
        self.screen.blit(
            self.small_font.render(f"LIVES {self.player.lives}", True, (90, 255, 90)),
            (18, SCREEN_HEIGHT - 32),
        )
        self.screen.blit(
            self.small_font.render(f"WAVE {self.wave}", True, (160, 160, 160)),
            (SCREEN_WIDTH - 110, SCREEN_HEIGHT - 32),
        )

    def _draw_game_over(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(
            self.font.render("GAME  OVER", True, (255, 90, 90)),
            (SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 - 22),
        )
        self.screen.blit(
            self.small_font.render("R — restart     ESC — quit", True, (220, 220, 220)),
            (SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 + 14),
        )

    def restart(self) -> None:
        self.score = ScoreSystem()
        self.wave = 1
        self.game_over = False
        self.alien_direction = 1
        self.alien_move_timer = self.alien_fire_timer = self.anim_timer = 0.0
        self.frame_toggle = False
        self.ufo = Ufo()
        self.ufo_spawn_timer = random.uniform(10.0, 18.0)
        self.ufo_popup = None
        self.player = Player(
            x=SCREEN_WIDTH / 2 - Player.WIDTH / 2,
            y=SCREEN_HEIGHT - 56,
            screen_width=SCREEN_WIDTH,
        )
        self.bullet = None
        self.fire_cooldown = 0.0
        self.alien_projectiles.clear()
        self.aliens = self._make_formation()
        self.shields = self._make_shields()


# ---------------------------------------------------------------------------
# Entry point — fixed-timestep loop
# ---------------------------------------------------------------------------

def main() -> None:
    game = Game()
    accumulator = 0.0

    running = True
    while running:
        frame_dt = min(game.clock.tick(120) / 1000.0, 0.25)
        accumulator += frame_dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game.game_over:
                    game.restart()

        while accumulator >= FIXED_DT:
            game.update(FIXED_DT)
            accumulator -= FIXED_DT

        game.draw()

    pygame.quit()


if __name__ == "__main__":
    main()
