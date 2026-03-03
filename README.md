# Space Invaders — Python + Pygame

Faithful modern recreation of the 1978 arcade game. Implements original mechanics: alien march cadence, row-based scoring, shield erosion, UFO mystery score, and single-bullet tension.

## Structure

| Path | Purpose |
|---|---|
| `main.py` | Entry point; fixed-timestep game loop |
| `entities/player.py` | Player ship — movement, lives, respawn |
| `entities/alien.py` | Alien sprite — row scoring, animation |
| `entities/bullet.py` | Player bullet — upward projectile |
| `entities/projectile.py` | Alien projectiles |
| `entities/shield.py` | Destructible shields with pixel erosion |
| `entities/ufo.py` | Mystery UFO |
| `systems/movement.py` | Alien formation march & cadence |
| `systems/collisions.py` | Hit detection (bullet/projectile vs alien/shield/player/UFO) |
| `systems/scoring.py` | Score, hi-score, UFO shot-sequence table |
| `systems/sound.py` | Optional `.wav` playback (silent if files absent) |

## Setup & Run

```bash
uv sync
uv run main.py
```

## Controls

| Key | Action |
|---|---|
| `←` / `→` | Move left / right |
| `Space` | Fire (one bullet at a time) |
| `R` | Restart after game over |
| `Esc` | Quit |

## Optional Audio

Drop any of these into `assets/audio/` to enable sound (game runs silently without them):

`shoot.wav` · `alien_hit.wav` · `player_hit.wav` · `ufo.wav` · `ufo_hit.wav`
