"""Pathfinding using pathing maps."""
import pygame
from helpers import Coords, Obstacles, Settings, in_bounds, to_tile_id
from movement import MovementType, PathContext, PathContexts, Terrain
from pygame import Color
from pygame.freetype import Font
from tile_map import TileMap
from typing import Dict, List, Tuple


class NeighborMap:
    """Holds tile IDs of neighbors for each tile in a map."""

    def __init__(self, xdims: int, ydims: int) -> None:
        self.cardinal = {}
        self.diagonal = {}
        tid = 0

        for tid in range(ydims * xdims):
            ncard, ndiag = NeighborMap.neighbors(tid, xdims, ydims)
            self.cardinal[tid] = ncard
            self.diagonal[tid] = ndiag

    @staticmethod
    def neighbors(tid: int, xdims: int, ydims: int) -> Tuple[List[int], List[int]]:
        """Returns cardinal and diagonal neighbors to tile with ID `tid`."""
        div = tid % xdims
        n = tid - xdims
        w = tid - 1
        e = tid + 1
        s = tid + xdims
        nw = tid - xdims - 1
        ne = tid - xdims + 1
        sw = tid + xdims - 1
        se = tid + xdims + 1

        # X: left edge, right edge, or neither
        if div == 0:
            w = None
            nw = None
            sw = None
        elif div == xdims - 1:
            e = None
            ne = None
            se = None

        # Y: top edge, bottom edge, or neither
        if tid < xdims:
            n = None
            nw = None
            ne = None
        elif tid >= xdims * ydims - xdims:
            s = None
            sw = None
            se = None

        cardinal = [nb for nb in (n, w, e, s) if nb is not None]
        diagonal = [nb for nb in (nw, ne, sw, se) if nb is not None]

        return cardinal, diagonal


class PathMaps:
    """Holds a PathMap for each movement type."""

    def __init__(self, movement_type: MovementType) -> None:
        # TODO: create pathing contexts, and PathMap for each
        pass


class PathMap:
    """Holds PathTiles for a given movement type.

    Tiles are considered to be LOW with no blockers unless otherwise specified.
    """

    def __init__(
        self,
        context: PathContext,
        terrain_data: Dict[Tuple[int, int], Terrain],
        blockers: Dict[Tuple[int, int], Obstacles],
        settings: Settings,
    ) -> None:
        self.tiles: List[PathTile] = []
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
        # for tile in self.tiles:
        #     tile.set_neighbors_cardinal(pathmap, context)

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


#   ########  ########   ######   ########
#      ##     ##        ##           ##
#      ##     ######     ######      ##
#      ##     ##              ##     ##
#      ##     ########  #######      ##


def test_neighbors_in_bounds():
    """Ensures NeighborMap correctly gets in-bounds tiles."""
    xdims = 3
    ydims = 3

    expected_cardinal = {
        0: [1, 3],
        1: [0, 2, 4],
        2: [1, 5],
        3: [0, 4, 6],
        4: [1, 3, 5, 7],
        5: [2, 4, 8],
        6: [3, 7],
        7: [4, 6, 8],
        8: [5, 7],
    }
    expected_diagonal = {
        0: [4],
        1: [3, 5],
        2: [4],
        3: [1, 7],
        4: [0, 2, 6, 8],
        5: [1, 7],
        6: [4],
        7: [3, 5],
        8: [4],
    }

    actual = NeighborMap(xdims, ydims)

    assert actual.cardinal == expected_cardinal
    assert actual.diagonal == expected_diagonal


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

    from pprint import pprint

    nmap = NeighborMap(3, 3)
    pprint(nmap.cardinal)
    pprint(nmap.diagonal)

    # print(f"-- Cardinal Neighbors --")
    # for tid in range(9):
    #     print(f"TID: {tid}")
    #     cn = NeighborMap.cardinal_neighbors(tid, 3, 3)
    #     for nid in cn:
    #         print(f" NID: {nid}")
