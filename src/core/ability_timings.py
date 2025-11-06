from dataclasses import dataclass

from .constants import ALL_PHASES, DEFAULT_TIMING
from src.classes import Ability, List

from src.logging_config import get_logger_for_package

logger = get_logger_for_package(__package__.split('.')[-1])


@dataclass(frozen=True)
class AbilityWithSource:
    """
    Class holding an Ability with a source (Unit/Battle Traits/...), has the attributes ability: Ability and source: str
    """
    ability: Ability
    source: str

    @property
    def name(self):
        return self.ability.no_format_name

    @property
    def timing(self):
        return self.ability.no_format_timing

    @property
    def declare(self):
        return self.ability.no_format_declare

    @property
    def effect(self):
        return self.ability.no_format_effect

    @property
    def keywords(self):
        return self.ability.no_format_keywords

    @property
    def cost(self):
        spell_ident = "Spell"
        prayer_ident = "Prayer"

        if self.ability.cost is not None:
            if self.ability.keywords is None or (spell_ident not in self.ability.keywords and prayer_ident not in self.ability.keywords):
                value_ident = "CP cost"
            else:
                if spell_ident in self.ability.keywords:
                    value_ident = "Casting Value"
                else:
                    value_ident = "Chanting Value"

            return f"{value_ident}: {self.ability.cost}"

        return None


def get_abilities_grouped_by_timing(army_list: List) -> dict[str, list[AbilityWithSource]]:
    """
    Sorts the unique abilities for a given List object by timing.
    :param army_list: the List object for which to get the abilities grouped by timing.
    :return: dict containing a list of unique abilities for each timing.
    """
    sorted_ability_timings = {timing:[] for timing in ALL_PHASES}
    all_abilities = get_abilities_with_sources(army_list)

    for ability_with_source in all_abilities:
        # Check if the ability is passive and if not search for timing in the appropriate field
        if (match := next((t for t in sorted_ability_timings if t in ability_with_source.ability.type), None)) is not None:
            timing = match.strip()
        elif (match := next((t for t in sorted_ability_timings if t in ability_with_source.timing), None)) is not None:
            timing = match.strip()
        else:
            timing = DEFAULT_TIMING

        sorted_ability_timings[timing].append(ability_with_source)

    logger.debug("Finished sorting abilities by timings for army list %s", army_list.name)

    return {timing: list(set(abilities)) for timing, abilities in sorted_ability_timings.items()}


def get_abilities_with_sources(army_list: List) -> list[AbilityWithSource]:
    """
    Constructs AbilityWithSource instances based on a List object.
    :param army_list: the List object for which to construct AbilityWithSource instances.
    :return: list of AbilityWithSource instances.
    """
    abilities = []

    for trait in army_list.battle_traits:
        abilities.append(AbilityWithSource(trait, "Battle Traits"))

    if army_list.battle_formation:
        formation_name, formation_ability = army_list.battle_formation
        abilities.append(AbilityWithSource(formation_ability, f"Battle Formation: {formation_name}"))

    for lore_name, lore_abilities in army_list.lores.items():
        for lore_ability in lore_abilities:
            abilities.append(AbilityWithSource(lore_ability, f"Lore: {lore_name}"))

    for carrier, enhancements in army_list.enhancements.items():
        for enhancement in enhancements:
            if isinstance(enhancement, Ability):
                abilities.append(AbilityWithSource(enhancement, f"{carrier} (Enhancement)"))

    for unit in army_list.units:
        for unit_ability in unit.abilities:
            abilities.append(AbilityWithSource(unit_ability, f"{unit.name}"))

    return abilities


def get_abilities_grouped_w_o_any(army_list: List) -> dict[str, list[AbilityWithSource]]:
    """
    Merges the abilities with 'Any ...' timing into the respective timings and returns the abilities grouped by timing.
    :param army_list: the List object for which to group the abilities.
    :return: dict containing a list of unique abilities for each timing with 'Any ...' timings merged.
    """
    any_turn_ident = "Any"
    enemy_turn_ident = "Enemy"
    your_turn_ident = "Your"

    grouped_abilities = get_abilities_grouped_by_timing(army_list)
    updated_abilities ={}

    for timing, abilities in grouped_abilities.items():
        if any_turn_ident not in timing:
            updated_abilities.setdefault(timing, []).extend(abilities)
            continue

        your_timing = timing.replace(any_turn_ident, your_turn_ident)
        enemy_timing = timing.replace(any_turn_ident, enemy_turn_ident)

        updated_abilities.setdefault(your_timing, []).extend(abilities)
        updated_abilities.setdefault(enemy_timing, []).extend(abilities)

    return updated_abilities
