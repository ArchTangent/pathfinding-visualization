"""Terrain, movement costs, and movement types for 2D pathfinding."""
import json
from enum import IntEnum, IntFlag
from helpers import Direction, Settings
from typing import Dict, List, Tuple


class MovementType(IntEnum):
    """Defines the terrain in which an Actor can move."""

    TERRESTRIAL = 0
    SUBTERRANEAN = 1
    AMPHIBIOUS = 2
    DEEP_AMPHIBIOUS = 3
    AQUATIC = 4
    AERIAL = 5

    def to_index(self) -> int:
        """Converts movement type to index form."""
        match self:
            case MovementType.TERRESTRIAL:
                return 0
            case MovementType.SUBTERRANEAN:
                return 1
            case MovementType.AMPHIBIOUS:
                return 2
            case MovementType.DEEP_AMPHIBIOUS:
                return 3
            case MovementType.AQUATIC:
                return 4
            case MovementType.AERIAL:
                return 5

    def to_string(self) -> str:
        """Converts string to movement type."""
        match self:
            case MovementType.TERRESTRIAL:
                return "TERRESTRIAL"
            case MovementType.SUBTERRANEAN:
                return "SUBTERRANEAN"
            case MovementType.AMPHIBIOUS:
                return "AMPHIBIOUS"
            case MovementType.DEEP_AMPHIBIOUS:
                return "DEEP_AMPHIBIOUS"
            case MovementType.AQUATIC:
                return "AQUATIC"
            case MovementType.AERIAL:
                return "AERIAL"

    @staticmethod
    def from_string(s: str):
        """Converts string to movement type."""
        if s == "terrestrial":
            return MovementType.TERRESTRIAL
        if s == "subterranean":
            return MovementType.SUBTERRANEAN
        if s == "amphibious":
            return MovementType.AMPHIBIOUS
        if s == "deep_amphibious":
            return MovementType.DEEP_AMPHIBIOUS
        if s == "aquatic":
            return MovementType.AQUATIC
        if s == "aerial":
            return MovementType.AERIAL

        raise ValueError(f"Invalid string representation '{s}' of MovementType!")


class Features(IntFlag):
    """Terrain features. Restricted to particular terrain."""

    EMPTY = 0
    LOW_WALL = 1
    HIGH_WALL = 2
    ROUGH = 4
    LOOSE = 8
    SWAMP = 16
    WEEDS = 32
    REEF = 64

    def to_index(self) -> int:
        """Converts features to index form."""
        match self:
            case Features.EMPTY:
                return 0
            case Features.LOW_WALL:
                return 1
            case Features.HIGH_WALL:
                return 2
            case Features.ROUGH:
                return 3
            case Features.LOOSE:
                return 4
            case Features.SWAMP:
                return 5
            case Features.WEEDS:
                return 6
            case Features.REEF:
                return 7

    def to_string(self) -> str:
        """Converts features to string."""
        match self:
            case Features.EMPTY:
                return "EMPTY"
            case Features.LOW_WALL:
                return "UNDERGROUND"
            case Features.HIGH_WALL:
                return "WATER"
            case Features.ROUGH:
                return "DEEP"
            case Features.LOOSE:
                return "SHALLOW"
            case Features.SWAMP:
                return "SWAMP"
            case Features.WEEDS:
                return "WEEDS"
            case Features.REEF:
                return "REEF"

    @staticmethod
    def from_string(s: str):
        """Converts string to Features."""
        if s == "empty":
            return Features.EMPTY
        if s == "low_wall":
            return Features.LOW_WALL
        if s == "high_wall":
            return Features.HIGH_WALL
        if s == "rough":
            return Features.ROUGH
        if s == "loose":
            return Features.LOOSE
        if s == "swamp":
            return Features.SWAMP
        if s == "weeds":
            return Features.WEEDS
        if s == "reef":
            return Features.REEF

        raise ValueError(f"Invalid string representation '{s}' of Features!")


class Terrain(IntEnum):
    """Base terrain. Fundamental structure for pathfinding."""

    EMPTY = 0  # No terrain. An error if present in final map
    UNDERGROUND = 1  # Under solid ground or shallows
    UNDERWATER = 2  # Under deep water
    DEEP = 3  # Surface of deep water
    SHALLOW = 4  # Surface of shallow water
    FLAT = 5  # On flat ground (floor)
    LOW = 6  # On low elevation ground or lower stair (1/3 height, ~3ft)
    MEDIUM = 7  # On medium elevation ground or upper stair (2/3 height, ~6ft)
    HIGH = 8  # On high elevation ground (full height, ~9ft)
    LOW_WALL_N = 9  # Low height North wall in distinct node
    LOW_WALL_W = 10  # Low height West wall in distinct node
    HIGH_WALL_N = 11  # Full height North wall in distinct node
    HIGH_WALL_W = 12  # Full height West wall in distinct node
    AIR = 13  # Above ground or over a chasm

    def is_north_wall(self):
        """Returns `True` if this Terrain is a North wall variant."""
        match self:
            case Terrain.LOW_WALL_N | Terrain.HIGH_WALL_N:
                return True
            case _:
                return False

    def is_west_wall(self):
        """Returns `True` if this Terrain is a West wall variant."""
        match self:
            case Terrain.LOW_WALL_W | Terrain.HIGH_WALL_W:
                return True
            case _:
                return False

    def to_string(self) -> str:
        """Converts terrain to string."""
        match self:
            case Terrain.EMPTY:
                return "EMPTY"
            case Terrain.UNDERGROUND:
                return "UNDERGROUND"
            case Terrain.UNDERWATER:
                return "WATER"
            case Terrain.DEEP:
                return "DEEP"
            case Terrain.SHALLOW:
                return "SHALLOW"
            case Terrain.FLAT:
                return "FLAT"
            case Terrain.LOW:
                return "LOW"
            case Terrain.MEDIUM:
                return "MEDIUM"
            case Terrain.HIGH:
                return "HIGH"
            case Terrain.LOW_WALL_N:
                return "LOW_WALL_N"
            case Terrain.LOW_WALL_W:
                return "LOW_WALL_W"
            case Terrain.HIGH_WALL_N:
                return "HIGH_WALL_N"
            case Terrain.HIGH_WALL_W:
                return "HIGH_WALL_W"
            case Terrain.AIR:
                return "AIR"

    @staticmethod
    def from_string(s: str):
        """Converts string to terrain."""
        if s == "empty":
            return Terrain.EMPTY
        if s == "underground":
            return Terrain.UNDERGROUND
        if s == "underwater":
            return Terrain.UNDERWATER
        if s == "deep":
            return Terrain.DEEP
        if s == "shallow":
            return Terrain.SHALLOW
        if s == "flat":
            return Terrain.FLAT
        if s == "low":
            return Terrain.LOW
        if s == "medium":
            return Terrain.MEDIUM
        if s == "high":
            return Terrain.HIGH
        if s == "low_wall_n":
            return Terrain.LOW_WALL_N
        if s == "low_wall_w":
            return Terrain.LOW_WALL_W
        if s == "high_wall_n":
            return Terrain.HIGH_WALL_N
        if s == "high_wall_w":
            return Terrain.HIGH_WALL_W
        if s == "air":
            return Terrain.AIR

        raise ValueError(f"Invalid string representation '{s}' of Terrain!")

    @staticmethod
    def from_symbol(s: str):
        """Converts character symbol to terrain. Used for loading JSON map data."""
        if s == "D":
            return Terrain.DEEP
        if s == "S":
            return Terrain.SHALLOW
        if s == "F":
            return Terrain.FLAT
        if s == "L":
            return Terrain.LOW
        if s == "M":
            return Terrain.MEDIUM
        if s == "H":
            return Terrain.HIGH
        if s == "n":
            return Terrain.LOW_WALL_N
        if s == "w":
            return Terrain.LOW_WALL_W
        if s == "N":
            return Terrain.HIGH_WALL_N
        if s == "W":
            return Terrain.HIGH_WALL_W

        raise ValueError(f"Invalid symbol representation '{s}' of Terrain!")


class TerrainFlags(IntFlag):
    """Base terrain bitflags for use with PathContexts."""

    EMPTY = 0
    UNDERGROUND = 1
    UNDERWATER = 2
    DEEP = 4
    SHALLOW = 8
    FLAT = 16
    LOW = 32
    MEDIUM = 64
    HIGH = 128
    LOW_WALL_N = 256
    LOW_WALL_W = 512
    HIGH_WALL_N = 1024
    HIGH_WALL_W = 2048
    AIR = 4096
    ALL = 0b1111_1111_1111_1111_1111_1111_1111_1111

    @staticmethod
    def from_terrain(t: Terrain):
        """Converts terrain to terrainflagsbitflag representation.

        Notes:
        - `EMPTY` is zero and intersects nothing.
        - All other flags are 2 ** (Enum - 1) and have at least one bit set.
        """
        match t:
            case Terrain.EMPTY:
                return TerrainFlags.EMPTY
            case Terrain.UNDERGROUND:
                return TerrainFlags.UNDERGROUND
            case Terrain.UNDERWATER:
                return TerrainFlags.UNDERWATER
            case Terrain.DEEP:
                return TerrainFlags.DEEP
            case Terrain.SHALLOW:
                return TerrainFlags.SHALLOW
            case Terrain.FLAT:
                return TerrainFlags.FLAT
            case Terrain.LOW:
                return TerrainFlags.LOW
            case Terrain.MEDIUM:
                return TerrainFlags.MEDIUM
            case Terrain.HIGH:
                return TerrainFlags.HIGH
            case Terrain.LOW_WALL_N:
                return TerrainFlags.LOW_WALL_N
            case Terrain.LOW_WALL_W:
                return TerrainFlags.LOW_WALL_W
            case Terrain.HIGH_WALL_N:
                return TerrainFlags.HIGH_WALL_N
            case Terrain.HIGH_WALL_W:
                return TerrainFlags.HIGH_WALL_W
            case Terrain.AIR:
                return TerrainFlags.AIR


class TargetContext:
    """PathContext data specific to a target-cost pair, e.g. `Flat: {cost, allowing, blocking}`."""

    def __init__(
        self,
        cost: int,
        allowing: Dict[Direction, TerrainFlags],
        blocking: Dict[Direction, TerrainFlags],
    ) -> None:
        self.cost = cost
        self.allowing = allowing
        self.blocking = blocking

    @staticmethod
    def from_dict(dir_dict: Dict):
        """Creates a new `TargetContext` from a dict of cost, allowing, and blocking data.

        There is one target context for every (source, target, direction) combination within
        a PathContext.

        Notes:
        - allowing flags are permissive: if one flag intersects, the direction is allowed
        - blocking flags are restrictive: if one flag intersects, the direction is blocked
        - if no specific allowing flags given, allowing flags are set to ALL (fully permissive)
        """
        cost: int = dir_dict["cost"]
        allowing_data: List[Dict[str, List[str]]] = dir_dict["allowing"]
        blocking_data: List[Dict[str, List[str]]] = dir_dict["blocking"]
        allowing: Dict[Direction, TerrainFlags] = {}
        blocking: Dict[Direction, TerrainFlags] = {}

        for dir_dict in allowing_data:
            for dir_str, terrain_strs in dir_dict.items():
                allowing_flags = TerrainFlags.EMPTY
                direction = Direction.from_string(dir_str)

                for terrain_str in terrain_strs:
                    t = Terrain.from_string(terrain_str)
                    tf = TerrainFlags.from_terrain(t)
                    allowing_flags |= tf

                if allowing_flags == TerrainFlags.EMPTY:
                    allowing[direction] = TerrainFlags.ALL
                else:
                    allowing[direction] = allowing_flags

        for dir_dict in blocking_data:
            for dir_str, terrain_strs in dir_dict.items():
                blocking_flags = TerrainFlags.EMPTY
                direction = Direction.from_string(dir_str)

                for terrain_str in terrain_strs:
                    t = Terrain.from_string(terrain_str)
                    tf = TerrainFlags.from_terrain(t)
                    blocking_flags |= tf

                blocking[direction] = blocking_flags

        return TargetContext(cost, allowing, blocking)


class PathContext:
    """Defines valid source-target terrain pairings for a given movement type.

    `PathContext = { (src, tgt, dir): (cost, allowing, blocking) }`

    Where:
    - `src` = source Terrain (NodeType)
    - `tgt` = target Terrain (NodeType)
    - `dir` = direction (N, S, E, W, ...)
    - `cost` = base move cost
    - `allowing` = relative nodes that allow movement from src-tgt
    - `blocking` = relative nodes that block movement from src-tgt
    """

    def __init__(
        self, context: Dict[Tuple[Terrain, Terrain, Direction], TargetContext]
    ) -> None:
        self.inner = {}
        for src, tgt in context.items():
            self.inner[src] = tgt

    def __getitem__(self, key: Terrain) -> Terrain:
        return self.inner[key]

    @staticmethod
    def from_dict(ctx_data: Dict):
        """Creates a new `PathContext` from a dict of context data.

        Format for each PathContext under a given MovementType:
        ```json
        {
            "shallow": {
                "flat": {
                    "N": { "cost": 40 },
                    "S": { "cost": 40 },
                    "E": { "cost": 40 },
                    "W": { "cost": 40 }
                }
            },
            "flat": {
                "flat": {
                    "N": { "cost": 10 },
                    "S": { "cost": 10 },
                    "E": { "cost": 10 },
                    "W": { "cost": 10 },
                    "NE": { "cost": 14, "allowing": { "N": ["flat"], "E": ["flat"] } },
                    "NW": { "cost": 14, "allowing": { "N": ["flat"], "W": ["flat"] } },
                    "SE": { "cost": 14, "allowing": { "S": ["flat"], "E": ["flat"] } },
                    "SW": { "cost": 14, "allowing": { "S": ["flat"], "W": ["flat"] } }
                }
            }
        }
        ```
        """
        context = {}

        for src_terrain_str, tgt_dict in ctx_data.items():
            src_terrain = Terrain.from_string(src_terrain_str)

            for tgt_terrain_str, dir_dict in tgt_dict.items():
                tgt_terrain = Terrain.from_string(tgt_terrain_str)

                for dir_str, dir_dict in tgt_dict.items():
                    direction = Direction.from_string(dir_str)
                    target_context = TargetContext.from_dict(dir_dict)

                    context[(src_terrain, tgt_terrain, direction)] = target_context

        return PathContext(context)


class PathContexts:
    """Holds PathContexts by associated movement type.

    To get valid target terrain for a terrain, use: `PathContexts[MovementType][Terrain]`
    """

    def __init__(self, contexts: Dict[MovementType, PathContext]) -> None:
        self.inner = contexts

    def context(self, mvtype: MovementType) -> PathContext:
        return self.inner[mvtype]

    def values(self):
        return self.inner.values()

    def items(self):
        return self.inner.items()

    @staticmethod
    def from_json_file(fp: str):
        """Deserializes `PathContexts` from JSON file at path `fp`.

        JSON data is a {string: {string: {string: {string: {data}}} depth 4 dictionary.

        Output data is a {MovementType: {Terrain: TerrainBits}} dictionary, where
        terrain and terrain bits are in bitflag form.
        """
        with open(fp, "r", encoding="utf-8") as f:
            jdict = json.load(f)

        contexts = {}

        for move_type_str, ctx_data in jdict.items():
            move_type = MovementType.from_string(move_type_str)
            contexts[move_type] = PathContext.from_dict(ctx_data)

        return PathContexts(contexts)


class CostTable:
    """Costs for (a) terrain to terrain and (b) tile to feature movement.

    Requirements:
    - All possible source-target Terrain combinations.
    - All possible combinations of Features.
    """

    def __init__(
        self,
        terrain_costs: Dict[Tuple[Terrain, Terrain], int],
        feature_costs: Dict[Features, int],
    ) -> None:
        self.by_terrain = terrain_costs
        self.by_feature = feature_costs

    @staticmethod
    def from_json_file(folder_path: str):
        """Deserializes `MoveCostTable` from JSON file at `folder_path`, e.g. `gamedata/`.

        terrain_costs.json is a {string: {string: {string: int}}} dictionary.
        feature_costs.json is a {string: int} dictionary.
        features_groups.json is a [list[string]] list.

        terrain_costs is a {(Terrain, Terrain): int} dictionary.
        feature_costs is a {Features: int} dictionary.
        feature_groups is used to add valid combinations of features.
        """
        terrain_path = f"{folder_path}terrain_costs.json"
        feature_path = f"{folder_path}feature_costs.json"
        group_path = f"{folder_path}feature_groups.json"

        with open(terrain_path, "r", encoding="utf-8") as f:
            tdict = json.load(f)

        with open(feature_path, "r", encoding="utf-8") as f:
            fdict = json.load(f)

        with open(group_path, "r", encoding="utf-8") as f:
            glist = json.load(f)

        terrain_costs = {}
        feature_costs = {}

        for move_type_str, cost_data in tdict.items():
            move_type = MovementType.from_string(move_type_str)
            inner = {}

            for src_terrain_str, tgt_terrain_data in cost_data.items():
                src_terrain = Terrain.from_string(src_terrain_str)

                for tgt_terrain_str, cost in tgt_terrain_data.items():
                    tgt_terrain = Terrain.from_string(tgt_terrain_str)
                    inner[(tgt_terrain, src_terrain)] = cost

            terrain_costs[move_type] = inner

        for feature_str, cost in fdict.items():
            feature = Features.from_string(feature_str)
            feature_costs[feature] = cost

        for feature_list in glist:
            to_add = Features.EMPTY
            cost = 0

            for feature_str in feature_list:
                feature = Features.from_string(feature_str)
                to_add |= feature
                cost += feature_costs[feature]

            if to_add != Features.EMPTY:
                feature_costs[to_add] = cost

        return CostTable(terrain_costs, feature_costs)


#   ########  ########   ######   ########
#      ##     ##        ##           ##
#      ##     ######     ######      ##
#      ##     ##              ##     ##
#      ##     ########  #######      ##


def test_movement_type_from_string():
    """Ensures proper conversion of MovementType from string."""

    incoming = [
        "terrestrial",
        "subterranean",
        "amphibious",
        "deep_amphibious",
        "aquatic",
        "aerial",
    ]
    expected = [
        MovementType.TERRESTRIAL,
        MovementType.SUBTERRANEAN,
        MovementType.AMPHIBIOUS,
        MovementType.DEEP_AMPHIBIOUS,
        MovementType.AQUATIC,
        MovementType.AERIAL,
    ]

    for ix, s in enumerate(incoming):
        assert MovementType.from_string(s) == expected[ix]


if __name__ == "__main__":
    print(f"\n===== Movement =====")

    from pprint import pprint

    contexts = PathContexts.from_json_file("gamedata/contexts.json")
    for mvtype, pcontext in contexts.items():
        pprint(mvtype)
        pprint(pcontext.inner)

    testy = [1, 2, 4, 8]
    for t in testy:
        terr = Terrain(t)
        pprint(terr)

    move_costs = CostTable.from_json_file("gamedata/")
    for mvtype, data in move_costs.by_terrain.items():
        pprint(mvtype)
        pprint(data)
    pprint(move_costs.by_feature)
