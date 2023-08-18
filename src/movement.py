"""Terrain, movement costs, and movement types for 2D pathfinding."""
import json
from enum import IntEnum, IntFlag
from typing import Dict


class Terrain(IntFlag):
    """Base terrain. Fundamental structure for pathfinding."""

    UNDERGROUND = 1  # Under solid ground or shallows
    UNDERWATER = 2  # Under deep water
    DEEP = 4  # Surface of deep water
    SHALLOW = 8  # Surface of shallow water
    LOW = 16  # On low elevation ground (flat)
    MEDIUM = 32  # On medium elevation ground (hills)
    HIGH = 64  # On high elevation ground (mountains)
    AIR = 128  # Above ground or over a chasm

    def to_index(self) -> int:
        """Converts terrain to index form for movement classes."""
        match self:
            case Terrain.UNDERGROUND:
                return 0
            case Terrain.UNDERWATER:
                return 1
            case Terrain.DEEP:
                return 2
            case Terrain.SHALLOW:
                return 3
            case Terrain.LOW:
                return 4
            case Terrain.MEDIUM:
                return 5
            case Terrain.HIGH:
                return 6
            case Terrain.AIR:
                return 7

    @staticmethod
    def from_string(s: str):
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


class MovementType(IntEnum):
    """Defines the terrain in which an Actor can move."""

    TERRESTRIAL = 1
    SUBTERRANEAN = 2
    AMPHIBIOUS = 3
    DEEP_AMPHIBIOUS = 4
    AQUATIC = 5
    AERIAL = 6

    def to_index(self) -> int:
        """Converts terrain to index form for movement classes."""
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

    @staticmethod
    def from_string(s: str):
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


class PathContext:
    """Defines valid source-target terrain pairings for a given movement type.

    `PathContext = { source_terrain_bits: target_terrain_bits }`
    """

    def __init__(self, context: Dict) -> None:
        self.inner = context

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

    def __init__(self, contexts: Dict) -> None:
        self.inner = contexts

    def __getitem__(self, key: MovementType) -> PathContext:
        return self.inner[key]

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
    for mvtype, pcontext in contexts.inner.items():
        pprint(mvtype)
        pprint(pcontext.inner)
