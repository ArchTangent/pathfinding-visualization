"""Pathfinding using pathing maps."""
import pygame
from enum import Enum
from helpers import Obstructions, Coords, Settings
from pygame import Color
from pygame.freetype import Font
from tile_map import TileMap
from typing import Dict, Tuple

class Terrain(Enum):
    """Base terrain. Fundamental structure for pathfinding."""

    UNDERGROUND = 1, # Under solid ground or shallows
    UNDERWATER = 2, # Under deep water
    DEEP = 4, # Surface of deep water
    SHALLOW = 8, # Surface of shallow water
    LOW = 16, # On low elevation ground (flat)
    MEDIUM = 32, # On medium elevation ground (hills)
    HIGH = 64, # On high elevation ground (mountains)
    AIR = 128, # Above ground or over a chasm

#   ##    ##     ##     ########  ##    ##
#   ###  ###   ##  ##      ##     ####  ##
#   ## ## ##  ##    ##     ##     ## ## ##
#   ##    ##  ########     ##     ##  ####
#   ##    ##  ##    ##  ########  ##    ##

if __name__ == "__main__":
    print(f"===== PathMap =====\n")
    
    pygame.freetype.init()

    blocked: Dict[Tuple[int, int], Obstructions] = {
        (4, 4): Obstructions(wall_n=2),
        (5, 4): Obstructions(wall_w=2),
        (8, 4): Obstructions(wall_n=2, wall_w=2),
        (10, 4): Obstructions(wall_n=2),
        (11, 4): Obstructions(wall_n=2),
        (13, 7): Obstructions(structure=True),
        (14, 6): Obstructions(structure=True),
        (15, 0): Obstructions(wall_w=2),
        (15, 1): Obstructions(wall_n=2),
        (19, 4): Obstructions(wall_n=2),
        (20, 3): Obstructions(wall_w=2),
        (20, 4): Obstructions(wall_n=2, wall_w=2),
    }

    settings = Settings(
        1280,
        720,
        Coords(16, 9),
        Font(None, size=16),
        Color("snow"),
        radius=5,
    )

    tilemap = TileMap(blocked, settings)
