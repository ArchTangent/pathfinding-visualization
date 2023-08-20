"""Pathfinding using pathing maps."""
import pygame
from helpers import Coords, Obstacles, Settings, in_bounds, to_tile_id
from movement import MovementType, PathContext, PathContexts, Terrain, TerrainData
from pygame import Color
from pygame.freetype import Font
from tile_map import TileMap
from typing import Dict, List, Optional, Self, Tuple


class Neighbors:
    """Holds optional Tile IDs for a tile's neighbors."""

    __slots__ = "NW", "N", "NE", "W", "E", "SW", "S", "SE"

    def __init__(self, nw, n, ne, w, e, sw, s, se) -> None:
        self.NW: Optional[int] = nw
        self.N: Optional[int] = n
        self.NE: Optional[int] = ne
        self.W: Optional[int] = w
        self.E: Optional[int] = e
        self.SW: Optional[int] = sw
        self.S: Optional[int] = s
        self.SE: Optional[int] = se

    @staticmethod
    def empty():
        return Neighbors(None, None, None, None, None, None, None, None)


class NeighborMap:
    """Holds tile IDs of neighbors for each tile in a map."""

    def __init__(self, xdims: int, ydims: int) -> None:
        self.inner = {}
        tid = 0

        for tid in range(ydims * xdims):
            self.inner[tid] = NeighborMap.neighbors(tid, xdims, ydims)

    # def __getitem__(self, key: int) -> List[Optional[int]]:
    def __getitem__(self, key: int) -> Neighbors:
        return self.inner[key]

    @staticmethod
    def neighbors(tid: int, xdims: int, ydims: int) -> Neighbors:
        """Returns cardinal and diagonal neighbors to tile with ID `tid`."""
        div = tid % xdims
        nw = tid - xdims - 1
        n = tid - xdims
        ne = tid - xdims + 1
        w = tid - 1
        e = tid + 1
        sw = tid + xdims - 1
        s = tid + xdims
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

        return Neighbors(nw, n, ne, w, e, sw, s, se)


class PathMaps:
    """Holds a PathMap for each movement type."""

    def __init__(self, contexts: PathContexts) -> None:
        # TODO: create pathing contexts, and PathMap for each MovementType in PathingContexts
        # TODO: create pathing contexts, and PathMap for each MovementType in PathingContexts
        pass


class PathMap:
    """Holds PathTiles for a given movement type.

    Tiles are considered to be LOW with no blockers unless otherwise specified.
    """

    def __init__(
        self,
        terrain_data: TerrainData,
        blockers: Dict[Tuple[int, int], Obstacles],
        neighbors: NeighborMap,
        context: PathContext,
        settings: Settings,
    ) -> None:
        self.tiles: List[PathTile] = []
        self.xdims = settings.xdims
        self.ydims = settings.ydims

        # Populate PathTiles with Terrain
        for y in range(settings.ydims):
            for x in range(settings.xdims):
                terrain = terrain_data[(x,y)]
                obstacles = blockers.get((x, y), Obstacles())
                tile = PathTile(terrain, obstacles)
                self.tiles.append(tile)

        # Find valid neighbors for each PathTile
        valid_neighbors: Dict[int, Neighbors] = {}

        for tid, tile in enumerate(self.tiles):
            nbrs = neighbors[tid]
            valid = Neighbors.empty()

            if nbrs.NW and tile.has_valid_neighbor(self.tiles, nbrs.NW, context):
                valid.NW = nbrs.NW
            if nbrs.N and tile.has_valid_neighbor(self.tiles, nbrs.N, context):
                valid.N = nbrs.N
            if nbrs.NE and tile.has_valid_neighbor(self.tiles, nbrs.NE, context):
                valid.NE = nbrs.NE
            if nbrs.W and tile.has_valid_neighbor(self.tiles, nbrs.W, context):
                valid.W = nbrs.W
            if nbrs.E and tile.has_valid_neighbor(self.tiles, nbrs.E, context):
                valid.E = nbrs.E
            if nbrs.SW and tile.has_valid_neighbor(self.tiles, nbrs.SW, context):
                valid.SW = nbrs.SW
            if nbrs.S and tile.has_valid_neighbor(self.tiles, nbrs.S, context):
                valid.S = nbrs.S
            if nbrs.SE and tile.has_valid_neighbor(self.tiles, nbrs.SE, context):
                valid.SE = nbrs.SE

            valid_neighbors[tid] = valid

        # Insert valid neighbors for each PathTile
        for tid, nbrs in valid_neighbors.items():
            tile = self.tiles[tid]
            tile.NW = nbrs.NW
            tile.N = nbrs.N
            tile.NE = nbrs.NE
            tile.W = nbrs.W
            tile.E = nbrs.E
            tile.SW = nbrs.SW
            tile.S = nbrs.S
            tile.SE = nbrs.SE


class PathTile:
    """Terrain, obstructions, and neighbors for a pathfinding tile and movement type.

    Notes:
    - `NW` to `SE` are the 8 neighbors, stored in TID order.
    - `above` and `below` indicate Air terrain above and Underground/Underwater below.
    - each movement type has its own PathMap and PathTiles.
    """

    __slots__ = (
        "terrain",
        "structure",
        "wall_n",
        "wall_w",
        "NW",
        "N",
        "NE",
        "W",
        "E",
        "SW",
        "S",
        "SE",
        "above",
        "below",
    )

    def __init__(self, terrain: Terrain, obstacles: Obstacles) -> None:
        """Create a new instance."""
        self.terrain: int = terrain.value
        self.structure = obstacles.structure
        self.wall_n = obstacles.wall_n
        self.wall_w = obstacles.wall_w
        self.NW: Optional[int] = None
        self.N: Optional[int] = None
        self.NE: Optional[int] = None
        self.W: Optional[int] = None
        self.E: Optional[int] = None
        self.SW: Optional[int] = None
        self.S: Optional[int] = None
        self.SE: Optional[int] = None
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

    def has_valid_neighbor(
        self, tiles: List[Self], nid: int, context: PathContext
    ) -> bool:
        """Returns `True` if tile at ID `nid` is a valid neighbor.

        Neighbor is valid if source terrain's valid terrain intersects target terrain.
        In other words, source-target connection is a valid pathing context.
        """
        src_terrain = self.terrain
        tgt_terrain = tiles[nid].terrain

        return context[src_terrain] & tgt_terrain > 0


#    ######      ##     ##         ######
#   ##    ##   ##  ##   ##        ##    ##
#   ##        ##    ##  ##        ##
#   ##    ##  ########  ##        ##    ##
#    ######   ##    ##  ########   ######
#     

def shortest_path(pathmap: PathMap) -> Optional[List]:
    """Returns tiles and cost along shortest path from source to target tile.
    
    If no valid path to target, returns `None`.

    Uses the `PathMap` assigned to the Actor that is moving. This is based on the 
    Actor's movement class (terrestrial, amphibious, etc..
    """
    # TODO: finish
    # TODO: add features
    # TODO: climbing over low and high walls (ht 1 and 2)

#   ##    ##     ##     ########  ##    ##
#   ###  ###   ##  ##      ##     ####  ##
#   ## ## ##  ##    ##     ##     ## ## ##
#   ##    ##  ########     ##     ##  ####
#   ##    ##  ##    ##  ########  ##    ##

if __name__ == "__main__":
    print(f"===== PathMap =====\n")

    pygame.freetype.init()  # type: ignore

    settings = Settings(
        1280,
        720,
        Coords(8, 5),
        Font(None, size=16),
        Color("snow"),
    )

    terrain_map = [
        "LLLSDSLL",
        "LLLSDSLL",
        "LLSSDSLL",
        "LSDDDSLL",
        "LSDSSLLL",
        "LSDSLLLL"
    ]

    terrain_data = TerrainData.from_map_data(terrain_map, settings)

    obstacle_data: Dict[Tuple[int, int], Obstacles] = {
        (3, 0): Obstacles(structure=2),
    }

    tilemap = TileMap(obstacle_data, settings)

    # TODO: XDIMS/YDIMS from terrain_map
    # TODO: tile size to 32?
    # TODO: add terrain to TileMap
    # TODO: add colors for terrain to Settings
    # TODO: update draw_tile() for terrain
    # TODO: build and draw TileMap

    from pprint import pprint

    nmap = NeighborMap(3, 3)
    pprint(nmap.neighbors)

    # print(f"-- Cardinal Neighbors --")
    # for tid in range(9):
    #     print(f"TID: {tid}")
    #     cn = NeighborMap.cardinal_neighbors(tid, 3, 3)
    #     for nid in cn:
    #         print(f" NID: {nid}")
            