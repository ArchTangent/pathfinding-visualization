"""Pathfinding using pathing maps."""
import pygame
from collections import deque
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

        Neighbor is valid if  target terrain is a valid destination for source
        terrain (by context).
        """
        src_terrain = self.terrain
        tgt_terrain = tiles[nid].terrain

        return context[src_terrain] & tgt_terrain > 0

    def has_valid_neighbor_n(self, tgt: Self, context: PathContext) -> bool:
        """Returns `True` if target tile is a valid neighbor to the North.

        Neighbor is valid if:
        - Target terrain is a valid destination for source terrain (by context)
        - Source tile `self` has no North wall
        """
        if context[self.terrain] & tgt.terrain == 0:
            return False
        if self.wall_n:
            return False

        return True

    def has_valid_neighbor_s(self, tgt: Self, context: PathContext) -> bool:
        """Returns `True` if target tile is a valid neighbor to the South.

        Neighbor is valid if:
        - Target terrain is a valid destination for source terrain (by context)
        - Target tile `tgt` has no North wall
        """
        if context[self.terrain] & tgt.terrain == 0:
            return False
        if tgt.wall_n:
            return False

        return True

    def has_valid_neighbor_e(self, tgt: Self, context: PathContext) -> bool:
        """Returns `True` if target tile is a valid neighbor to the East.

        Neighbor is valid if:
        - Target terrain is a valid destination for source terrain (by context)
        - Target tile `tgt` has no West wall
        """
        if context[self.terrain] & tgt.terrain == 0:
            return False
        if tgt.wall_w:
            return False

        return True

    def has_valid_neighbor_w(self, tgt: Self, context: PathContext) -> bool:
        """Returns `True` if target tile is a valid neighbor to the West.

        Neighbor is valid if:
        - Target terrain is a valid destination for source terrain (by context)
        - Source tile `self` has no West wall
        """
        if context[self.terrain] & tgt.terrain == 0:
            return False
        if self.wall_w:
            return False

        return True

    def has_valid_neighbor_nw(
        self, tgt: Self, n: Optional[Self], w: Optional[Self], context: PathContext
    ) -> bool:
        """Returns `True` if target tile is a valid neighbor to the Northwest.

        Neighbor is valid if:
        - Target terrain is a valid destination for source terrain (by context)
        - Source tile `self` has no North wall or West Wall
        - North tile `n` has no West wall or Structure
        - West tile `w` has no North wall or Structure
        """
        if context[self.terrain] & tgt.terrain == 0:
            return False
        if self.wall_n or self.wall_w:
            return False
        if n and (n.structure or n.wall_w):
            return False
        if w and (w.structure or w.wall_n):
            return False

        return True

    def has_valid_neighbor_ne(
        self, tgt: Self, n: Optional[Self], e: Optional[Self], context: PathContext
    ) -> bool:
        """Returns `True` if target tile is a valid neighbor to the Northeast.

        Neighbor is valid if:
        - Target terrain is a valid destination for source terrain (by context)
        - Source tile `self` has no North wall
        - Target tile `tgt` has no West wall
        - North tile `n` has no Structure
        - East tile `e` has no North Wawll, West wall or Structure
        """
        if context[self.terrain] & tgt.terrain == 0:
            return False
        if self.wall_n:
            return False
        if tgt.wall_w:
            return False
        if n and n.structure:
            return False
        if e and (e.structure or e.wall_n or e.wall_w):
            return False

        return True

    def has_valid_neighbor_sw(
        self, tgt: Self, s: Optional[Self], w: Optional[Self], context: PathContext
    ) -> bool:
        """Returns `True` if target tile is a valid neighbor to the Southwest.

        Neighbor is valid if:
        - Target terrain is a valid destination for source terrain (by context)
        - Source tile `self` has no West wall
        - Target tile `tgt` has no North wall
        - South tile `s` has no North wall, West wall or Structure
        - West tile `w` has no Structure
        """
        if context[self.terrain] & tgt.terrain == 0:
            return False
        if self.wall_w:
            return False
        if tgt.wall_n:
            return False
        if s and (s.structure or s.wall_n or s.wall_w):
            return False
        if w and w.structure:
            return False

        return True

    def has_valid_neighbor_se(
        self, tgt: Self, s: Optional[Self], e: Optional[Self], context: PathContext
    ) -> bool:
        """Returns `True` if target tile is a valid neighbor to the Southeast.

        Neighbor is valid if:
        - Target terrain is a valid destination for source terrain (by context)
        - Target tile `tgt` has no North wall or West wall
        - South tile `s` has no North wall or Structure
        - East tile `e` has no West wall or Structure
        """
        if context[self.terrain] & tgt.terrain == 0:
            return False
        if tgt.wall_n or tgt.wall_w:
            return False
        if s and (s.structure or s.wall_n):
            return False
        if e and (e.structure or e.wall_w):
            return False

        return True


class PathMap:
    """Holds PathTiles for a given movement type."""

    def __init__(
        self,
        terrain_data: TerrainData,
        blockers: Dict[Tuple[int, int], Obstacles],
        neighbors: NeighborMap,
        ctx: PathContext,
        settings: Settings,
    ) -> None:
        self.tiles: List[PathTile] = []
        self.xdims = settings.xdims
        self.ydims = settings.ydims

        for y in range(settings.ydims):
            for x in range(settings.xdims):
                terrain = terrain_data[(x, y)]
                obstacles = blockers.get((x, y), Obstacles())
                tile = PathTile(terrain, obstacles)
                self.tiles.append(tile)

        self.set_valid_neighbors(neighbors, ctx)

    def set_valid_neighbors(self, neighbors: NeighborMap, ctx: PathContext):
        """Sets valid neighbors for each PathTile in the PathMap."""
        valid_neighbors = get_valid_neighbors(self.tiles, neighbors, ctx)

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

    def tile(self, tid: int):
        """Returns the PathTile with given tile ID."""
        return self.tiles[tid]


class PathMaps:
    """Holds a PathMap for each movement type."""

    def __init__(self, contexts: PathContexts) -> None:
        # TODO: create pathing contexts, and PathMap for each MovementType in PathingContexts
        # TODO: create pathing contexts, and PathMap for each MovementType in PathingContexts
        pass


def get_valid_neighbors(
    tiles: List[PathTile], neighbors: NeighborMap, ctx: PathContext
) -> Dict[int, Neighbors]:
    """Returns dictionary of valid neighbors for each tile.

    Target tile is not a valid neighbor if:
    - source-target pair is not a valid pathing context OR
    - target is diagonal (NW, NE, SW, SE) and an adjacent cardinal tile has a
      blocking wall of any height
    """
    valid_neighbors: Dict[int, Neighbors] = {}

    for tid, tile in enumerate(tiles):
        valid = Neighbors.empty()
        nbrs = neighbors[tid]
        N = tiles[nbrs.N] if nbrs.N else None
        S = tiles[nbrs.S] if nbrs.S else None
        E = tiles[nbrs.E] if nbrs.E else None
        W = tiles[nbrs.W] if nbrs.W else None
        NW = tiles[nbrs.NW] if nbrs.NW else None
        NE = tiles[nbrs.NE] if nbrs.NE else None
        SW = tiles[nbrs.SW] if nbrs.SW else None
        SE = tiles[nbrs.SE] if nbrs.SE else None

        if NW and tile.has_valid_neighbor_nw(NW, N, W, ctx):
            valid.NW = nbrs.NW
        if N and tile.has_valid_neighbor_n(N, ctx):
            valid.N = nbrs.N
        if NE and tile.has_valid_neighbor_ne(NE, N, E, ctx):
            valid.NE = nbrs.NE
        if W and tile.has_valid_neighbor_w(W, ctx):
            valid.W = nbrs.W
        if E and tile.has_valid_neighbor_e(E, ctx):
            valid.E = nbrs.E
        if SW and tile.has_valid_neighbor_sw(SW, S, W, ctx):
            valid.SW = nbrs.SW
        if S and tile.has_valid_neighbor_s(S, ctx):
            valid.S = nbrs.S
        if SE and tile.has_valid_neighbor_se(SE, S, E, ctx):
            valid.SE = nbrs.SE

        valid_neighbors[tid] = valid

    return valid_neighbors


#    ######      ##     ##         ######
#   ##    ##   ##  ##   ##        ##    ##
#   ##        ##    ##  ##        ##
#   ##    ##  ########  ##        ##    ##
#    ######   ##    ##  ########   ######


def shortest_path(pathmap: PathMap) -> Optional[List]:
    """Returns tiles and cost along shortest path from source to target tile.

    If no valid path to target, returns `None`.

    Uses the `PathMap` assigned to the Actor that is moving. This is based on the
    Actor's movement class (terrestrial, amphibious, etc..
    """
    # TODO: finish
    # TODO: add features
    # TODO: climbing over low and high walls (ht 1 and 2)
    path = []


def breadth_first_search(pathmap: PathMap, src: int, tgt: int):
    """Returns depth where target is first found, or None if not found."""
    if src == tgt:
        return 0

    # Queue of (node, depth) pairs
    # to_search = deque([(edge, 1) for edge in pathmap])


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
        "LSDSLLLL",
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
