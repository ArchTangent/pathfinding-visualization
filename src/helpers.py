"""Helper classes and functions for pathfinding visualization."""
from collections.abc import Iterator
from enum import Enum
from pygame import Color
from pygame.freetype import Font


class Coords:
    """2D map integer coordinates."""

    __slots__ = "x", "y"

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __iter__(self):
        return iter((self.x, self.y))

    def __repr__(self) -> str:
        return f"{self.x, self.y}"

    def as_tuple(self):
        return (self.x, self.y)


class Colors:
    """Defines colors for pathfinding visualization."""

    def __init__(
        self,
        font_normal="snow",
        font_reserve="yellow2",
        font_over="tomato2",
        floor="steelblue2",
        floor_trim="steelblue4",
        fov_line="deepskyblue1",
        wall="slategray2",
        wall_trim="slategray3",
        structure="slategray2",
        structure_trim="slategray3",
        # wall="seagreen3",
        # wall_trim="seagreen4",
        # structure="seagreen3",
        # structure_trim="seagreen4",
        underground="chocolate4",
        underwater="midnightblue",
        deep="blue2",
        shallow="deepskyblue1",
        low="seagreen2",
        medium="seagreen3",
        high="seagreen4",
        air="slategray1",
    ) -> None:
        # --- Fonts --- #
        self.font_normal = Color(font_normal)
        self.font_reserve = Color(font_reserve)
        self.font_over = Color(font_over)
        # --- Tiles --- #
        self.floor = Color(floor)
        self.floor_trim = Color(floor_trim)
        self.fov_line = Color(fov_line)
        self.wall = Color(wall)
        self.wall_trim = Color(wall_trim)
        self.structure = Color(structure)
        self.structure_trim = Color(structure_trim)

        # --- Terrain --- #
        self.underground = Color(underground)
        self.underwater = Color(underwater)
        self.deep = Color(deep)
        self.shallow = Color(shallow)
        self.low = Color(low)
        self.medium = Color(medium)
        self.high = Color(high)
        self.air = Color(air)


class Direction(Enum):
    """Ten-way directions for 2D Pathing."""

    N = 1
    S = 2
    E = 3
    W = 4
    NE = 5
    NW = 6
    SE = 7
    SW = 8
    ABOVE = 9
    BELOW = 10

    @staticmethod
    def from_string(s: str):
        match s:
            case "N":
                return Direction.N
            case "S":
                return Direction.S
            case "E":
                return Direction.E
            case "W":
                return Direction.W
            case "NE":
                return Direction.NE
            case "NW":
                return Direction.NW
            case "SE":
                return Direction.SE
            case "SW":
                return Direction.SW
            case "above":
                return Direction.ABOVE
            case "below":
                return Direction.BELOW
            case _:
                raise ValueError(f"Invalid string representation '{s}' of Direction!")


class Settings:
    """Settings for Pathfinding and pygame."""

    def __init__(
        self,
        width: int,
        height: int,
        map_dims: Coords,
        font: Font,
        colors: Colors,
    ) -> None:
        if map_dims.x < 1 or map_dims.y < 1:
            raise ValueError("all map dimensions must be > 0!")

        self.width = width
        self.height = height
        self.xdims, self.ydims = map_dims
        self.font = font
        self.colors = colors


def in_bounds(x: int, y: int, xdims: int, ydims: int) -> bool:
    """Returns `True` if tile is in bounds."""
    return x >= 0 and x < xdims and y >= 0 and y < ydims


def to_tile_id(x: int, y: int, xdims: int):
    """Takes 2D tile (x,y) coordinates and converts them into a tile ID.

    Parameters
    ---
    `x, y` : int
        (x,y) coordinates of the tile.
    `xdims` : int
        number of x dimensions.
    """
    return x + y * xdims
