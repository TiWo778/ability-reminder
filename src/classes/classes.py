from dataclasses import dataclass, asdict
import json

@dataclass(frozen=True)
class Ability:
    """
    Represents an ability, has attributes name: str, type: str, timing: str | None, keywords: str | None, declare: str | None, effect: str, cost: str | None
    """
    name: str
    type: str
    timing: str | None
    keywords: str | None
    declare: str | None
    effect: str
    cost: str | None # This field may contain command point cost or casting/chanting value depending on the ability type

    def to_json(self):
        """
        Parses self to JSON
        """
        return json.dumps(asdict(self))
    
    @property
    def no_format_name(self):
        """
        Get name without formatting substrings
        :return: name without formatting substrings
        """
        return self.name.replace("^^", "").replace("**", "")
    
    @property
    def no_format_timing(self):
        """
        Get timing without formatting substrings
        :return: timing without formatting substrings
        """
        if self.timing is None:
            return None
        
        return self.timing.replace("^^", "").replace("**", "")

    @property
    def no_format_declare(self):
        """
        Get declare without formatting substrings
        :return: declare without formatting substrings
        """
        if self.declare is None:
            return None

        return self.declare.replace("^^", "").replace("**", "")

    @property
    def no_format_effect(self):
        """
        Get effect without formatting substrings
        :return: effect without formatting substrings
        """
        return self.effect.replace("^^", "").replace("**", "")

    @property
    def no_format_keywords(self):
        """
        Get keywords without formatting substrings
        :return: keywords without formatting substrings
        """
        if self.keywords is None:
            return None

        return self.keywords.replace("^^", "").replace("**", "")

@dataclass(frozen=True)
class Weapon:
    """
    Represents a Weapon profile, has attributes: name: str, type: str, range: str | None, attacks: str, hit: str, wound: str, rend: str, damage: str, keywords: str | None
    """
    name: str
    type: str
    range: str | None
    attacks: str
    hit: str
    wound: str
    rend: str
    damage: str
    keywords: str | None

    def to_json(self):
        """
        Parses self to JSON
        """
        return json.dumps(asdict(self))


@dataclass(frozen=True)
class Unit:
    """
    Represents a unit profile, has attributes: name: str, move: str, health: str, control: str | None, banishment: str | None, save: str, keywords: str | None, weapons: list[Weapon], abilities: list[Ability]
    """
    name: str
    move: str
    health: str
    control: str | None
    banishment: str | None
    save: str
    keywords: str | None
    weapons: list[Weapon]
    abilities: list[Ability]

    def to_json(self):
        """
        Parses self to JSON
        """
        return json.dumps(asdict(self))


@dataclass(frozen=True)
class Faction:
    """
    Represents a faction, has attributes: name: str, battle_traits: list[Ability], battle_formations: dict[str,Ability] | None, enhancements_available: dict[str,list[Ability]], lores_available: dict[str,list[Ability]], units: list[Unit]
    """
    name: str
    battle_traits: list[Ability]
    battle_formations: dict[str,Ability] | None
    enhancements_available: dict[str,list[Ability]]
    lores_available: dict[str,list[Ability]]
    units: list[Unit]

    def to_json(self):
        """
        Parses self to JSON
        """
        # Need to parse manually as dataclasses.asdict cannot handle nested dataclasses in dicts
        fac_dict = {
            "name": self.name,
            "battle_traits": [asdict(trait) for trait in self.battle_traits],
            "battle_formations": {
                formation_name: asdict(ability) for formation_name, ability in self.battle_formations.items()
            },
            "enhancements_available": {
                enhancement_group:
                    [asdict(enhancement) for enhancement in enhancements]
                for enhancement_group, enhancements in self.enhancements_available.items()
            },
            "lores_available": {
                lore:
                    [asdict(spell) for spell in spells]
                for lore, spells in self.lores_available.items()

            },
            "units": [asdict(unit) for unit in self.units]
        }

        return json.dumps(fac_dict)


@dataclass(frozen=True)
class List:
    """
    Represents an army list, has attributes: name: str battle_tactics: list[str] | None, faction: str, battle_traits: list[Ability], battle_formation: tuple[str,Ability] | None, enhancements: dict[str, list[Ability | str]], lores: dict[str,list[Ability]], units: list[Unit]
    """
    name: str
    battle_tactics: list[str] | None
    faction: str
    battle_traits: list[Ability]
    battle_formation: tuple[str,Ability] | None
    enhancements: dict[str, list[Ability | str]] # Also contains if a unit has been reinforced
    lores: dict[str,list[Ability]]
    units: list[Unit]

    def to_json(self):
        """
        Parses self to JSON
        """
        # Need to parse manually as dataclasses.asdict cannot handle nested dataclasses in dicts
        fac_dict = {
            "name": self.name,
            "battle_tactics": self.battle_tactics,
            "faction": self.faction,
            "battle_traits": [asdict(trait) for trait in self.battle_traits],
            "battle_formation": {self.battle_formation[0]: asdict(self.battle_formation[1])} if self.battle_formation else {},
            "enhancements": {
                carrier: [
                    asdict(enhancement)
                    if not isinstance(enhancement, str) else enhancement
                    for enhancement in enhancements]
                for carrier, enhancements in self.enhancements.items()
            },
            "lores": {
                lore:
                    [asdict(spell) for spell in spells]
                for lore, spells in self.lores.items()

            },
            "units": [asdict(unit) for unit in self.units]
        }

        return json.dumps(fac_dict)
