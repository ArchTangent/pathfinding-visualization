"""Pathfinding using pathing maps."""
import pygame
from helpers import Coords, Obstacles, Settings
from movement import MovementType, PathContext, Terrain
from pygame import Color
from pygame.freetype import Font
from tile_map import TileMap
from typing import Dict, Tuple


class PathMaps:
    """Holds a PathMap for each movement type."""

    def __init__(self) -> None:
        # TODO: create pathing contexts, and PathMap for each
        pass


class PathMap:
    """Holds PathTiles for a given movement type.

    Tiles are considered to be LOW with no blockers unless otherwise specified.
    """

    def __init__(
        self,
        terrain_data: Dict[Tuple[int, int], Terrain],
        blockers: Dict[Tuple[int, int], Obstacles],
        settings: Settings,
    ) -> None:
        self.tiles = []
        self.xdims = settings.xdims
        self.ydims = settings.ydims

        for y in range(settings.ydims):
            for x in range(settings.xdims):
                terrain = terrain_data.get((x, y), Terrain.LOW)
                obstacles = blockers.get((x, y), Obstacles())
                tile = PathTile(terrain, obstacles)
                self.tiles.append(tile)

        # TODO: set valid neighbors for each tile
        # Set valid neighbors

    def in_bounds(self, x: int, y: int) -> bool:
        return x > 0 and x < self.xdims and y > 0 and y < self.ydims


class PathTile:
    """Terrain, obstructions, and neighbors for a pathfinding tile and movement type.

    Notes:
    - `cardinal` and `diagonal` are the 8 neighbors in given directions.
    - `above` and `below` indicate Air terrain above and Underground/Underwater below.
    - each movement type has its own PathMap and PathTiles.
    """

    __slots__ = (
        "terrain",
        "structure",
        "wall_n",
        "wall_w",
        "cardinal",
        "diagonal",
        "above",
        "below",
    )

    def __init__(self, terrain: Terrain, obstacles: Obstacles) -> None:
        self.terrain = terrain.value
        self.structure = obstacles.structure
        self.wall_n = obstacles.wall_n
        self.wall_w = obstacles.wall_w
        self.cardinal = []
        self.diagonal = []
        self.above: int
        self.below: int

        match terrain:
            case Terrain.UNDERGROUND:
                raise ValueError("UNDERGROUND is an invalid base terrain!")
            case Terrain.UNDERWATER:
                raise ValueError("UNDERWATER is an invalid base terrain!")
            case Terrain.DEEP:
                self.above = Terrain.AIR.value
                self.below = Terrain.UNDERWATER.value
            case Terrain.SHALLOW:
                self.above = Terrain.AIR.value
                self.below = Terrain.UNDERGROUND.value
            case Terrain.LOW:
                self.above = Terrain.AIR.value
                self.below = Terrain.UNDERGROUND.value
            case Terrain.MEDIUM:
                self.above = Terrain.AIR.value
                self.below = Terrain.UNDERGROUND.value
            case Terrain.HIGH:
                self.above = Terrain.AIR.value
                self.below = Terrain.UNDERGROUND.value
            case Terrain.AIR:
                raise ValueError("AIR is an invalid base terrain!")

    def set_neighbors_cardinal(self, pathmap: PathMap, context: PathContext):
        """Sets valid NSEW neighbors by their tile ID (TID)."""
        # TODO: check all in-bounds neighbors for valid src->tgt pahting context

    def set_neighbors_diagonal(self, pathmap: PathMap, context: PathContext):
        """Sets valid NSEW neighbors by their tile ID (TID)."""
        # TODO: check all in-bounds neighbors for valid src->tgt pahting context


#   ##    ##     ##     ########  ##    ##
#   ###  ###   ##  ##      ##     ####  ##
#   ## ## ##  ##    ##     ##     ## ## ##
#   ##    ##  ########     ##     ##  ####
#   ##    ##  ##    ##  ########  ##    ##

if __name__ == "__main__":
    print(f"===== PathMap =====\n")

    pygame.freetype.init()  # type: ignore

    blocked: Dict[Tuple[int, int], Obstacles] = {
        (4, 4): Obstacles(wall_n=2),
        (5, 4): Obstacles(wall_w=2),
        (8, 4): Obstacles(wall_n=2, wall_w=2),
        (10, 4): Obstacles(wall_n=2),
        (11, 4): Obstacles(wall_n=2),
        (13, 7): Obstacles(structure=True),
        (14, 6): Obstacles(structure=True),
        (15, 0): Obstacles(wall_w=2),
        (15, 1): Obstacles(wall_n=2),
        (19, 4): Obstacles(wall_n=2),
        (20, 3): Obstacles(wall_w=2),
        (20, 4): Obstacles(wall_n=2, wall_w=2),
    }

    settings = Settings(
        1280,
        720,
        Coords(16, 9),
        Font(None, size=16),
        Color("snow"),
    )

    tilemap = TileMap(blocked, settings)

    # TODO: tile size to 32?
    # TODO: add terrain to TileMap
    # TODO: add colors for terrain to Settings
    # TODO: update draw_tile() for terrain
    # TODO: build and draw TileMap
