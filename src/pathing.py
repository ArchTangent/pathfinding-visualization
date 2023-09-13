"""Pathfinding using pathing maps."""
import json
import pygame
from collections import OrderedDict
from enum import Enum
from heapq import heappush, heappop
from helpers import Colors, Coords, Settings
from movement import (
    Features,
    MovementType,
    PathContext,
    PathContexts,
    Terrain,
)
from pygame.freetype import Font
from typing import Dict, List, Optional, Self, Tuple


class Location:
    """Stores NodeID and Terrain for a `LocationMap`."""

    def __init__(self, nid: int, terrain: Terrain) -> None:
        self.nid = nid
        self.terrain = terrain


class LocationMap:
    """Maps (x,y) coordinates to node ID and Terrain for creation of a `PathMap`.

    Notes:
    - Updates Node ID (nid) for each valid Node (Tile, West Wall, North Wall) added.
    - No North walls placed where y == 0 (leads nowhere)
    - No West walls placed where x == 0 (leads nowhere)
    """

    def __init__(
        self,
    ) -> None:
        self.nid = 0
        self.tiles: OrderedDict[Tuple[int, int], Location] = OrderedDict()
        self.walls_n: Dict[Tuple[int, int], Location] = {}
        self.walls_w: Dict[Tuple[int, int], Location] = {}

    def insert(self, x: int, y: int, terrain: Terrain):
        """Inserts new node into location map based on Terrain type (Tile, N/W wall)."""
        if terrain.is_north_wall():
            if y > 0:
                self.walls_n[(x, y)] = Location(self.nid, terrain)
                self.nid += 1
        elif terrain.is_west_wall():
            if x > 0:
                self.walls_w[(x, y)] = Location(self.nid, terrain)
                self.nid += 1
        else:
            self.tiles[(x, y)] = Location(self.nid, terrain)
            self.nid += 1

    def get_tile_id(self, x: int, y: int) -> Optional[int]:
        """Returns tile Node ID at given coordinates, or None if not present."""
        location = self.tiles.get((x, y))
        return location.nid if location else None

    def get_tile(self, x: int, y: int) -> Optional[Location]:
        """Returns tile Location at given coordinates, or None if not present."""
        return self.tiles.get((x, y))

    def get_north_wall_id(self, x: int, y: int) -> Optional[int]:
        """Returns wall Nod ID at given coordinates, or None if not present."""
        location = self.walls_n.get((x, y))
        return location.nid if location else None

    def get_north_wall(self, x: int, y: int) -> Optional[Location]:
        """Returns wall Location at given coordinates, or None if not present."""
        return self.walls_n.get((x, y))

    def get_west_wall_id(self, x: int, y: int) -> Optional[int]:
        """Returns wall Node ID at given coordinates, or None if not present."""
        location = self.walls_n.get((x, y))
        return location.nid if location else None

    def get_west_wall(self, x: int, y: int) -> Optional[Location]:
        """Returns wall Location at given coordinates, or None if not present."""
        return self.walls_w.get((x, y))

    def tile_items(self):
        """Returns tiles dictionary items, in order added."""
        return self.tiles.items()

    @staticmethod
    def from_json_file(fp: str, settings: Settings):
        """Creates a `LocationMap` JSON file at path `fp`from list of strings.

        Example `map_data.json`:
        ```json
        {
            "tiles" = [
                "LLLSDSLL",
                "LLLSDSLL",
                "LLSSDSLL",
                "LSDDDSLL",
                "LSDSSLLL",
                "LSDSLLLL"
            ],
            "walls": {
                "1,0": ["high_wall_w"],
                "3,1": ["high_wall_n","high_wall_w"]
            }
        }
        ```
        """
        xdims, ydims = settings.xdims, settings.ydims
        location_map = LocationMap()

        with open(fp, "r", encoding="utf-8") as f:
            jdict = json.load(f)

        tiles = jdict["tiles"]
        walls: Dict[Tuple[int, int], List[Terrain]] = {}

        for coords, wall_strs in jdict["walls"].items():
            x, y = coords.split(",")
            walls[(int(x), int(y))] = [Terrain.from_string(w) for w in wall_strs]

        if len(tiles) != ydims:
            raise ValueError(f"{fp}: Y dimensions don't match settings!")

        for y, str_row in enumerate(tiles):
            if len(str_row) != xdims:
                raise ValueError(f"{fp}:  dimensions don't match settings!")

            for x, terrain_char in enumerate(str_row):
                terrain = Terrain.from_symbol(terrain_char)

                location_map.insert(x, y, terrain)

                for wall_node in walls.get((x, y), []):
                    location_map.insert(x, y, wall_node)

        return location_map


class Neighbor:
    """Data for tile ID, terrain cost, and terrain features for a Tile neighbor.

    `features` is a bitflag representing zero or more terrain features in the neighbor.
    """

    def __init__(
        self, nid: int, terrain_cost: int, feature_cost: int, features: Features
    ) -> None:
        self.neighbor_id = nid
        self.terrain_cost = terrain_cost
        self.feature_cost = feature_cost
        self.features = features


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


class Node:
    """Terrain (NodeType) and neighbors for a pathfinding tile and movement type.

    Notes:
    - If neighbor is invalid (e.g. out of bounds), the value is `None`.
    - `above` and `below` indicate Air terrain above and Underground/Underwater below.
    - each movement type has its own NodeCosts and CostTable.
    """

    __slots__ = (
        "x",
        "y",
        "terrain",
        "features",
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

    def __init__(
        self,
        x: int,
        y: int,
        terrain: Terrain,
        features: Features,
        N: Optional[int] = None,
        S: Optional[int] = None,
        E: Optional[int] = None,
        W: Optional[int] = None,
        NW: Optional[int] = None,
        NE: Optional[int] = None,
        SW: Optional[int] = None,
        SE: Optional[int] = None,
    ) -> None:
        """Create a new instance."""
        self.x = x
        self.y = y
        self.terrain = terrain
        self.features = features
        self.N = N
        self.S = S
        self.E = E
        self.W = W
        self.NW = NW
        self.NE = NE
        self.SW = SW
        self.SE = SE
        self.above: Terrain
        self.below: Terrain

        match terrain:
            case Terrain.EMPTY:
                raise ValueError("EMPTY is an invalid base terrain!")
            case Terrain.UNDERGROUND:
                raise ValueError("UNDERGROUND is an invalid base terrain!")
            case Terrain.UNDERWATER:
                raise ValueError("UNDERWATER is an invalid base terrain!")
            case Terrain.AIR:
                raise ValueError("AIR is an invalid base terrain!")
            case Terrain.DEEP:
                self.above = Terrain.AIR
                self.below = Terrain.UNDERWATER
            case _:
                self.above = Terrain.AIR
                self.below = Terrain.UNDERGROUND

    @staticmethod
    def tile(x: int, y: int, t: Terrain, f: Features, location_map: LocationMap):
        """Creates new Tile (not a wall) instance.

        Rules:
        - No NW, N, or NE neighbor when y = 0
        - No SW, S, or SE neighbor when y = ymax
        - No NW, W, or SW neighbor when x = 0
        - No SE, E, or SE neighbor when x = xmax
        - Cardinal neighbors can be tiles or walls
        - Diagonal neighbors can only be tiles
        """
        # North wall in own tile, or tile to North
        N = location_map.get_north_wall_id(x, y)
        if N is None:
            N = location_map.get_tile_id(x, y - 1)

        # North wall in tile to South, or tile to South
        S = location_map.get_north_wall_id(x, y + 1)
        if S is None:
            S = location_map.get_tile_id(x, y + 1)

        # West wall in tile to East, or tile to East
        E = location_map.get_west_wall_id(x + 1, y)
        if E is None:
            E = location_map.get_tile_id(x + 1, y)

        # West wall in own tile, or tile to West
        W = location_map.get_west_wall_id(x, y)
        if W is None:
            W = location_map.get_tile_id(x - 1, y)

        # Tiles only for diagonal neighbors
        NW = location_map.get_tile_id(x - 1, y - 1)
        NE = location_map.get_tile_id(x + 1, y - 1)
        SW = location_map.get_tile_id(x - 1, y + 1)
        SE = location_map.get_tile_id(x + 1, y + 1)

        return Node(x, y, t, f, N, S, E, W, NW, NE, SW, SE)

    @staticmethod
    def north_wall(x: int, y: int, t: Terrain, f: Features, location_map: LocationMap):
        """Creates new North wall instance.

        Rules:
        - Not placed where y = 0 (should not even be in the LocationMap)
        - N and S neighbors only
        - Neighbors can only be tiles
        """
        N = location_map.get_tile_id(x, y - 1)
        S = location_map.get_tile_id(x, y + 1)

        return Node(x, y, t, f, N=N, S=S)

    @staticmethod
    def west_wall(x: int, y: int, t: Terrain, f: Features, location_map: LocationMap):
        """Creates new West wall instance.

        Rules:
        - Not placed where x = 0 (should not even be in the LocationMap)
        - E and W neighbors only
        - Neighbors can only be tiles
        """
        E = location_map.get_tile_id(x + 1, y)
        W = location_map.get_tile_id(x - 1, y)

        return Node(x, y, t, f, E=E, W=W)

    def coords(self) -> Tuple[int, int]:
        """Returns (x,y) coordinates of this Node."""
        return (self.x, self.y)

    def edges(self) -> List[int]:
        """Returns tile IDs of all valid neighbors of this Node."""
        return [
            edge
            for edge in (
                self.NW,
                self.NE,
                self.SW,
                self.SE,
                self.N,
                self.W,
                self.E,
                self.S,
            )
            if edge
        ]

    def edges_cardinal(self) -> List[int]:
        """Returns tile IDs of all valid cardinal neighbors of this PathTile."""
        return [
            edge
            for edge in (
                self.N,
                self.W,
                self.E,
                self.S,
            )
            if edge
        ]

    def edges_diagonal(self) -> List[int]:
        """Returns tile IDs of all valid diagonal neighbors of this PathTile."""
        return [
            edge
            for edge in (
                self.NW,
                self.NE,
                self.SW,
                self.SE,
            )
            if edge
        ]

    def has_valid_neighbor_n(self, tgt: Self, context: PathContext) -> bool:
        """Returns `True` if target tile is a valid neighbor to the North.

        Neighbor is valid if:
        - Target terrain is a valid destination for source terrain (by context)
        - Source tile `self` has no North wall
        """
        if context[self.terrain] & tgt.terrain == 0:
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

        return True

    def has_valid_neighbor_e(self, tgt: Self, context: PathContext) -> bool:
        """Returns `True` if target tile is a valid neighbor to the East.

        Neighbor is valid if:
        - Target terrain is a valid destination for source terrain (by context)
        - Target tile `tgt` has no West wall
        """
        if context[self.terrain] & tgt.terrain == 0:
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

        return True


class PathMap:
    """Holds `Node` instances for all tiles and walls in a map. Used for all movement types.

    Initialization:
    1. Iterate over each tile's (x,y): Location in ordered LocationMap
    2. Create Node with data from step (1)
    3. Append Node to PathMap
    4. Add any North and West walls associated with (x,y) coordinates
    """

    def __init__(
        self,
        location_map: LocationMap,
        settings: Settings,
    ) -> None:
        self.nodes: List[Node] = []
        self.xdims = settings.xdims
        self.ydims = settings.ydims

        for (x, y), location in location_map.tile_items():
            tile = Node.tile(x, y, location.terrain, Features.EMPTY, location_map)
            self.nodes.append(tile)

            north_wall = location_map.get_north_wall(x, y)
            if north_wall:
                wall_n = Node.north_wall(
                    x, y, location.terrain, Features.EMPTY, location_map
                )
                self.nodes.append(wall_n)

            west_wall = location_map.get_west_wall(x, y)
            if west_wall:
                wall_w = Node.west_wall(
                    x, y, location.terrain, Features.EMPTY, location_map
                )
                self.nodes.append(wall_w)

    def node(self, tid: int):
        """Returns the Node with given node ID."""
        return self.nodes[tid]


def get_valid_neighbors(
    tiles: List[Node], neighbors: NeighborMap, ctx: PathContext
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


def breadth_first_search_depth(pathmap: PathMap, src: int, tgt: int) -> Optional[int]:
    """Returns depth where target `tgt` is first found, or None if not found.

    Uses a FIFO queue of (node, depth) pairs where nodes to search are pulled
    from front, and new edges are added to the back.
    """
    if src == tgt:
        return 0

    print(f"[BFS_depth] from {src} to {tgt}")

    curr = []
    next = []

    seen = {src}
    depth = 1

    for edge in pathmap.node(src).edges():
        curr.append(edge)
        seen.add(edge)

    while curr:
        while curr:
            node = curr.pop()

            if node == tgt:
                return depth

            for edge in pathmap.node(node).edges():
                if edge not in seen:
                    next.append(edge)
                    seen.add(edge)

        depth += 1
        curr, next = next, curr

    return None


def breadth_first_search(pathmap: PathMap, src: int, tgt: int) -> Optional[List[int]]:
    """Returns path of TIDs along an unweighted breadth first search, or None if not found.

    Uses a FIFO queue of (node, depth) pairs where nodes to search are pulled
    from front, and new edges are added to the back.
    """
    if src == tgt:
        return [0]

    print(f"[BFS_path] from {src} to {tgt}")

    seen: Dict[int, Optional[int]] = {src: None}
    curr = []
    next = []

    for edge in pathmap.node(src).edges():
        curr.append(edge)
        seen[edge] = src

    while curr:
        while curr:
            node = curr.pop()

            if node == tgt:
                path = []
                to_node = node

                while to_node:
                    from_node = seen[to_node]
                    path.append(to_node)
                    to_node = from_node

                path.append(src)
                return path

            for edge in pathmap.node(node).edges():
                if edge not in seen:
                    next.append(edge)
                    seen[edge] = node

        curr, next = next, curr

    return None


# def a_star(pathmap: PathMap, src: int, tgt: int) -> Optional[List[Tuple[int, int]]]:
#     """A* algorithm returning path and cost from source to target, or None if not found.

#     Notes:
#     - Actual cost (TUs) is used for the real path.
#     - Heuristic is abs(dx) + abs(dy) and is only used for priority.
#     - The `queue` is a min heap of `(priority, tid)` pairs.
#     - The `origin_of` dict holds `{to_node: from_node}` pairs.
#     - The `total_cost` dict holds `{to_node: running_cost}` pairs.
#     """
#     if src == tgt:
#         return [0]

#     print(f"[AStar] from {src} to {tgt}")

#     origin_of = {}
#     total_cost = {src: int(0)}
#     queue = []
#     tx, ty = pathmap.tile(tgt).coords()

#     # TODO: get cost using Terrain and Features (separate costs)
#     while queue:
#         _priority, node_id = heappop(queue)

#         if node_id == tgt:
#             path = [(tgt, total_cost[tgt])]
#             to_id = node_id

#             # TODO: finish path reconstruction
#             while to_id:
#                 from_id = origin_of[to_id]
#                 path.append((to_id, total_cost[to_id]))
#                 to_id = from_id

#             return path

#         node = pathmap.tile(node_id)

#         # Diagonal movement doesn't account for walls

#         # Cardinal movement accounts for walls

#         for edge_id in pathmap.tile(node_id).edges():
#             # TODO: cost from node to edge (next node)
#             edge = pathmap.tile(edge_id)
#             edge_cost = total_cost[edge_id] + movement_cost(node, edge)

#             if edge_id not in total_cost or edge_cost < total_cost[edge_id]:
#                 total_cost[edge_id] = edge_cost
#                 origin_of[edge_id] = node_id
#                 ex, ey = pathmap.tile(edge_id).coords()
#                 priority = edge_cost + abs(tx - ex) + abs(ty - ey)
#                 heappush(queue, (priority, edge_id))

#     return None


# # TODO: separate calc for Diagonal and Cardinal neighbors (cardinal uses walls)
# # TODO: add features and terrain/feature bonus
# def movement_cost(src: PathTile, tgt: PathTile) -> int:
#     """Returns movement cost from source to target tile.

#     Cost is based on movement type, terrain, features, and modifiers.
#     Base cost is based on the target tile only.
#     """


#   ##    ##     ##     ########  ##    ##
#   ###  ###   ##  ##      ##     ####  ##
#   ## ## ##  ##    ##     ##     ## ## ##
#   ##    ##  ########     ##     ##  ####
#   ##    ##  ##    ##  ########  ##    ##

if __name__ == "__main__":
    print(f"===== PathMap =====\n")

    pygame.freetype.init()  # type: ignore

    colors = Colors()

    settings = Settings(1280, 720, Coords(8, 6), Font(None, size=16), colors)

    location_map = LocationMap.from_json_file("gamedata/map_data.json", settings)
    path_contexts = PathContexts.from_json_file("gamedata/path_contexts.json")

    mvtype = MovementType.TERRESTRIAL
    pathmap = PathMap(location_map, settings)

    src = 0
    tgt = 47
    print(f"--- BFS ---")
    bfs = breadth_first_search_depth(pathmap, src, tgt)
    bfs_p = breadth_first_search(pathmap, src, tgt)
    print(f"from {src} to {tgt} for {mvtype.to_string()}:")
    print(f"  bfs: {bfs}")
    print(f"  bfs_path: {bfs_p}")

    mvtype = MovementType.AMPHIBIOUS
    bfs = breadth_first_search_depth(pathmap, src, tgt)
    bfs_p = breadth_first_search(pathmap, src, tgt)
    print(f"from {src} to {tgt} for {mvtype.to_string()}:")
    print(f"  bfs: {bfs}")
    print(f"  bfs_path: {bfs_p}")

    # TODO: load terrain_costs into NodeCosts
    # TODO: make PathMap and LocationMap from JSON with terrrain_data obstacle_data
    # TODO: build LocationMap from PathMap
    # TODO: build NodeCosts for each MovementType using PathMap and LocationMap
    # TODO: build CostTable for each MovementType using PathMap and NodeCosts
