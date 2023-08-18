"""Helper classes and functions for pathfinding visualization."""
from pygame import Color
from pygame.freetype import Font


class Obstacles:
    """Walls and structures in a tile."""

    def __init__(
        self,
        structure: int = 0,
        wall_n: int = 0,
        wall_w: int = 0,
    ) -> None:
        self.structure = structure
        self.wall_n = wall_n
        self.wall_w = wall_w


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


class Settings:
    """Settings for Pathfinding and pygame."""

    def __init__(
        self,
        width: int,
        height: int,
        map_dims: Coords,
        font: Font,
        font_color: Color,
        floor_color="steelblue2",
        floor_trim_color="steelblue4",
        fov_line_color="deepskyblue1",
        wall_color="seagreen3",
        wall_trim_color="seagreen4",
        structure_color="seagreen3",
        structure_trim_color="seagreen4",
    ) -> None:
        if map_dims.x < 1 or map_dims.y < 1:
            raise ValueError("all map dimensions must be > 0!")

        self.width = width
        self.height = height
        self.xdims, self.ydims = map_dims
        self.font = font
        self.font_color = font_color
        self.floor_color = Color(floor_color)
        self.fov_line_color = fov_line_color
        self.floor_trim_color = Color(floor_trim_color)
        self.wall_color = Color(wall_color)
        self.wall_trim_color = Color(wall_trim_color)
        self.structure_color = Color(structure_color)
        self.structure_trim_color = Color(structure_trim_color)


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
