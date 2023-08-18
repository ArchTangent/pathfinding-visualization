"""Tile map with terrain, walls, and structures."""
from typing import Dict, Tuple
from helpers import Obstacles, Coords, Settings, to_tile_id
from pygame import Vector2


class Tile:
    """2D Tile, where `p1` is the reference point for drawing."""

    def __init__(self, tid: int, coords: Coords, ts: int, blockers: Obstacles):
        self.tid = tid
        self.x = coords.x
        self.y = coords.y
        self.p1 = Vector2(coords.x * ts, coords.y * ts)
        self.structure = blockers.structure
        self.wall_n = blockers.wall_n
        self.wall_w = blockers.wall_w

    def __repr__(self) -> str:
        return f"T{self.tid}({self.x},{self.y}) S:{self.structure} N: {self.wall_n} W: {self.wall_w}"

    def to_coords(self) -> Tuple[int, int]:
        return (self.x, self.y)


class TileMap:
    """2D tilemap with terrain, structures and walls."""

    def __init__(
        self,
        blocked_tiles: Dict[Tuple[int, int], Obstacles],
        settings: Settings,
    ):
        ts = 64
        xdims, ydims = settings.xdims, settings.ydims
        self.xdims = xdims
        self.ydims = ydims
        self.tiles = [
            Tile(
                to_tile_id(x, y, xdims),
                Coords(x, y),
                ts,
                blocked_tiles.get((x, y), Obstacles()),
            )
            for y in range(ydims)
            for x in range(xdims)
        ]

    def tile_at(self, x: int, y: int) -> Tile:
        """Gets Tile at given location."""
        tid = x + y * self.xdims
        return self.tiles[tid]
