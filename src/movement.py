"""Terrain, movement costs, and movement types for 2D pathfinding."""
import json
from enum import IntEnum, IntFlag
from helpers import Settings
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

        raise ValueError("Invalid string representation of MovementType!")


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

        raise ValueError("Invalid string representation of Features!")


class Terrain(IntFlag):
    """Base terrain. Fundamental structure for pathfinding."""

    EMPTY = 0  # No terrain
    UNDERGROUND = 1  # Under solid ground or shallows
    UNDERWATER = 2  # Under deep water
    DEEP = 4  # Surface of deep water
    SHALLOW = 8  # Surface of shallow water
    LOW = 16  # On low elevation ground (flat)
    MEDIUM = 32  # On medium elevation ground (hills)
    HIGH = 64  # On high elevation ground (mountains)
    AIR = 128  # Above ground or over a chasm

    def to_index(self) -> int:
        """Converts terrain to index form."""
        match self:
            case Terrain.EMPTY:
                return 0
            case Terrain.UNDERGROUND:
                return 1
            case Terrain.UNDERWATER:
                return 2
            case Terrain.DEEP:
                return 3
            case Terrain.SHALLOW:
                return 4
            case Terrain.LOW:
                return 5
            case Terrain.MEDIUM:
                return 6
            case Terrain.HIGH:
                return 7
            case Terrain.AIR:
                return 8

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
            case Terrain.LOW:
                return "LOW"
            case Terrain.MEDIUM:
                return "MEDIUM"
            case Terrain.HIGH:
                return "HIGH"
            case Terrain.AIR:
                return "AIR"

    @staticmethod
    def from_string(s: str):
        """Converts string to terrain."""
        if s == "underground":
            return Terrain.UNDERGROUND
        if s == "underwater":
            return Terrain.UNDERWATER
        if s == "deep":
            return Terrain.DEEP
        if s == "shallow":
            return Terrain.SHALLOW
        if s == "low":
            return Terrain.LOW
        if s == "medium":
            return Terrain.MEDIUM
        if s == "high":
            return Terrain.HIGH
        if s == "air":
            return Terrain.AIR

        raise ValueError("Invalid string representation of Terrain!")


class TerrainData:
    """Terrain for a pathing map."""

    def __init__(self, terrain_data: Dict[Tuple[int, int], Terrain]) -> None:
        self.inner = {coords: t for coords, t in terrain_data.items()}

    def __getitem__(self, key: Tuple[int, int]):
        return self.inner[key]

    @staticmethod
    def from_map_data(terrain_map: List[str], settings: Settings):
        """Creates `TerrainData` from list of strings.

        Example input (8x6):
        ```
        terrain_map = [
            "LLLSDSLL",
            "LLLSDSLL",
            "LLSSDSLL",
            "LSDDDSLL",
            "LSDSSLLL",
            "LSDSLLLL"
        ]
        ```
        """
        terrain_data = {}
        xdims, ydims = settings.xdims, settings.ydims

        if len(terrain_map) != ydims:
            raise ValueError("Terrain map Y dimensions don't match settings!")

        for y, str_row in enumerate(terrain_map):
            if len(str_row) != xdims:
                raise ValueError("Terrain map X dimensions don't match settings!")

            for x, terrain_char in enumerate(str_row):
                match terrain_char:
                    case "L":
                        t = Terrain.LOW
                    case "M":
                        t = Terrain.MEDIUM
                    case "H":
                        t = Terrain.HIGH
                    case "S":
                        t = Terrain.SHALLOW
                    case "D":
                        t = Terrain.DEEP
                    case _:
                        raise ValueError("Invalid Terrain character in terrain map!")

                terrain_data[(x, y)] = t

        return TerrainData(terrain_data)


class PathContext:
    """Defines valid source-target terrain pairings for a given movement type.

    `PathContext = { source_terrain_bits: target_terrain_bits }`
    """

    def __init__(self, context: Dict[Terrain, Terrain]) -> None:
        self.inner = {t: Terrain.EMPTY for t in Terrain}
        for src, tgt in context.items():
            self.inner[src] = tgt

    def __getitem__(self, key: Terrain) -> Terrain:
        return self.inner[key]

    @staticmethod
    def from_dict(ctx_data: Dict):
        """Creates a new `PathContext` from a dict of {src_string: List[tgt_string]} pairs."""
        context = {}

        for src_terrain_str, tgt_terrains_str in ctx_data.items():
            src_terrain = Terrain.from_string(src_terrain_str)
            tgt_terrain = 0

            for t_str in tgt_terrains_str:
                tgt_t = Terrain.from_string(t_str)
                tgt_terrain |= tgt_t

            context[src_terrain] = tgt_terrain

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

        JSON data is a {string: {string: [string, string, ...]}} dictionary.

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


class MoveCostTable:
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

        Terrain costs is a {string: {string: {string: int}}} dictionary.
        """
        terrain_path = f"{folder_path}terrain_costs.json"
        feature_path = f"{folder_path}feature_costs.json"

        with open(terrain_path, "r", encoding="utf-8") as f:
            tdict = json.load(f)

        with open(feature_path, "r", encoding="utf-8") as f:
            fdict = json.load(f)

        terrain_costs = {}
        feature_costs = {}

        for move_type_str, cost_data in tdict.items():
            move_type = MovementType.from_string(move_type_str)
            depth1 = {}

            for src_terrain_str, tgt_terrain_data in cost_data.items():
                src_terrain = Terrain.from_string(src_terrain_str)
                depth2 = {}

                for tgt_terrain_str, cost in tgt_terrain_data.items():
                    tgt_terrain = Terrain.from_string(tgt_terrain_str)
                    depth2[tgt_terrain] = cost
                
                depth1[src_terrain] = depth2

            terrain_costs[move_type] = depth1

        for feature_str, cost in fdict.items():
            feature = Features.from_string(feature_str)
            feature_costs[feature] = cost

        return MoveCostTable(terrain_costs, feature_costs)


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

    move_costs = MoveCostTable.from_json_file("gamedata/")
    for mvtype, data in move_costs.by_terrain.items():
        pprint(mvtype)
        pprint(data)
    pprint(move_costs.by_feature)