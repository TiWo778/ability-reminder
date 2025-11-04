import re

from src.data_loading.services import ParsingService
from src.classes import List, Faction

from src.logging_config import get_logger_for_package

logger = get_logger_for_package(__package__.split('.')[-1])


def parse_list(army_list: str, data_dir: str | None = None) -> List:
    """
    Method for parsing an army list given as text, using data located at data_dir.
    :param army_list: The text of the army list.
    :param data_dir: The data directory where the data is located, if it is None, uses the default data_dir of the used ParsingService. (Optional, defaults to None)
    :return: List object representing the parsed data.
    """
    list_dict = get_list_as_dict(army_list)
    parser = ParsingService()
    if data_dir:
        parser.change_data_location(data_dir)

    parser.load_faction(list_dict["faction"])
    parser.load_army_of_renown(list_dict["army_of_renown"])
    faction = parser.get_faction()

    battle_formation = (list_dict["battle_formation"], faction.battle_formations[list_dict["battle_formation"]]) \
        if faction.battle_formations and list_dict["battle_formation"] else None
    enhancements = get_enhancement_unit_dict(list_dict["units"], faction)

    lores_in_list = {_get_lore_name_without_ident(lore): lore for lore in list_dict["lores"]}
    lores_in_faction = {_get_lore_name_without_ident(lore): lore for lore in faction.lores_available}

    # Some Armies of Renown have different names in the official App than the dataset (The Knights of New Summercourt vs New Summercourt)
    lores = {}
    for faction_lore_no_ident, lore_name in lores_in_faction.items():
        for list_lore_no_ident in lores_in_list:
            if all(word in list_lore_no_ident for word in faction_lore_no_ident.split(" ")):
                lores[lore_name] = faction.lores_available[lore_name]

    units = get_unit_objects(list_dict["units"], faction)

    list_obj = List(
        list_dict["name"],
        list_dict["battle_tactics"],
        list_dict["faction"],
        faction.battle_traits,
        battle_formation,
        enhancements,
        lores,
        units
    )

    logger.debug("Created list object %s", list_obj.to_json())

    return list_obj


def get_unit_objects(units: list[str], faction: Faction, sep: str = " & ") -> list:
    """
    Extracts the Unit objects for the given unit names from a faction object.
    :param units: list of unit names.
    :param faction: faction object containing the unit objects.
    :param sep: the separator between the unit names (Optional, defaults to " & ").
    :return: list of unit objects.
    """
    unit_objs = []

    for unit in units:
        unit_objs.extend(list(filter(
            lambda u: u.name == unit.split(sep)[0],
            faction.units)))

    return unit_objs


def get_enhancement_unit_dict(units_with_enhancements: list[str], faction: Faction, sep: str = " & ") -> dict[str, list]:
    """
    Extracts which unit has which enhancement from a list of unit names with enhancement names
    :param units_with_enhancements: list of unit names with enhancements, separated by sep.
    :param faction: faction object containing the ability objects representing the enhancements.
    :param sep: the separator between the unit names (Optional, defaults to " & ").
    :return: dict with unit names as keys and lists of enhancement abilities as values.
    """
    unit_enhancement_dict = {}

    for unit_enhancement_str in units_with_enhancements:
        unit_enhancement_list = unit_enhancement_str.split(sep)
        unit = unit_enhancement_list[0]
        enhancement_names = unit_enhancement_list[1:]

        if not enhancement_names:
            continue

        enhancements = []
        for enhancement in enhancement_names:
            for _, abilities in faction.enhancements_available.items():
                enhancements.extend(list(filter(
                    lambda a: a.name == enhancement,
                    abilities
                )))

        unit_enhancement_dict[unit] = enhancements

    return unit_enhancement_dict


def get_list_as_dict(army_list: str) -> dict[str, list[str] | str | None]:
    """
    Parses a string army list into a dictionary.
    :param army_list: the text of the army list.
    :return: dict containing the respective fields in format {name: str, faction: str, army_of_renown: str | None, battle_formation: str, lores: list[str], battle_tactics: list[str], units: list[str]}.
    """
    soggy_ident = "Scourge of Ghyran"
    aor_ident = "Army of Renown"
    aor_splitter = " - "
    lore_ident = "Lore "
    tactics_ident = "Battle Tactic Cards"
    tactics_sep = ", "
    list_dict = {
        "name": None,
        "faction": None,
        "army_of_renown": None,
        "battle_formation": None,
        "lores": [],
        "battle_tactics": [],
        "units": []
    }

    cleaned_list = _remove_redundant_fields(_norm_list_text(army_list))
    lines = cleaned_list.splitlines()

    list_dict["name"] = lines[0]

    if aor_splitter in lines[1]:
        list_dict["faction"] = lines[1].split(aor_splitter)[0]
        list_dict["army_of_renown"] = lines[1].split(aor_splitter)[1]
        if aor_ident in lines[2]:
            iter_start_idx = 3
        else:
            iter_start_idx = 2
    elif aor_ident in lines:
        list_dict["faction"] = lines[1]
        list_dict["army_of_renown"] = lines[2]
        iter_start_idx = 4
    else:
        list_dict["faction"] = lines[1]

        if not lines[2].startswith(tactics_ident) and not lore_ident in lines[2]:
            list_dict["battle_formation"] = lines[2]
            iter_start_idx = 3
        else:
            iter_start_idx = 2

    for i in range(iter_start_idx, len(lines)):
        line = lines[i]

        if line.startswith(tactics_ident):
            list_dict["battle_tactics"] = line.replace(tactics_ident, "").replace(":", "").strip().split(tactics_sep)
        elif lore_ident in line:
            lore_name = line.replace("-", "").split(lore_ident, 1)[1].strip()
            if lore_name != "":
                list_dict["lores"].append(lore_name)
        else:
            if line.startswith(soggy_ident):

                list_dict["units"].append(remove_points(correct_alternate_warscroll_name(line, soggy_ident).strip()))
            list_dict["units"].append(remove_points(line.strip()))

    logger.debug("Finished parsing list %s to dictionary %s", list_dict["name"], str(list_dict))

    return list_dict


def correct_alternate_warscroll_name(text: str, ident: str) -> str:
    """
    Changes text in from *Alternate Warscroll Identifier Unit* to *Unit (Alternate Warscroll Identifier)*.
    :param text: the unit name to correct
    :param ident: the alternate warscroll identifier
    :return: corrected unit name
    """
    corrected = text.replace(ident, "").strip()
    return f"{corrected} ({ident})"


def remove_points(text: str) -> str:
    """
    Removes the point values from a unit text
    :param text: the unit text
    :return: the unit text without point values
    """
    # Remove parentheses containing point values as well as the optional - present in enhancements that cost points
    cleaned = re.sub(r"\s*\(\s*[-+]?\d+\s*\)\s*", " ", text)

    # Remove the Points text if it is present
    cleaned = re.sub(r"\s+Points", "", cleaned)

    # Remove unnecessary spaces
    cleaned = re.sub(r"\s+", " ", cleaned)  # normalize multiple spaces

    return cleaned.strip()


def _remove_redundant_fields(text: str) -> str:
    """
    Removes fields not relevant for list parsing from a text
    :param text: the text of the list
    :return: the cleaned text of the list
    """
    redundant_line_tokens = [
        "General's",
        "Drops",
        "Regiment",
        "Faction Terrain",
        "App",
        "Created",
        "Data",
        "Version",
        "Auxiliaries",
        "Wounds",
        "----",
        "Orruk Warclans"  # Temp fix as they are the only faction with split battletome
    ]

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    filtered_lines = [line for line in lines if not any(token in line for token in redundant_line_tokens)]
    cleaned_text = "\n".join(filtered_lines)

    return cleaned_text


def _norm_list_text(text: str) -> str:
    """
    Restore formatting of lists if newlines go missing (often happens when copying from the app)
    :param text: the list text to normalize
    :return: normalized list
    """
    alt_faction_separator = "|"
    field_separator = "\n"
    insert_after_tokens = ["pts"]
    insert_before_tokens = [
        "General\'s",
        "Drops",
        "Spell ",
        "Prayer ",
        "Manifestation ",
        "Battle Tactic ",
        "Regiment ",
        "Faction Terrain",
        "Created "]

    normed_text = text.replace(alt_faction_separator, field_separator)

    # Insert newlines where missing
    for substring in insert_after_tokens:
        normed_text = insert_after(normed_text, substring, field_separator)
    for substring in insert_before_tokens:
        normed_text = insert_before(normed_text, substring, field_separator)

    # Remove double spaces
    normed_text = normed_text.replace("  ", " ")

    # Attach unit modifiers to unit
    normed_text = replace_bullet_points(normed_text)

    return normed_text


def _get_lore_name_without_ident(lore_name: str) -> str:
    spell_ident = "Spell Lore"
    prayer_ident = "Prayer Lore"
    manifestation_ident = "Manifestation Lore"
    possible_sep = ":"

    if spell_ident in lore_name:
        new_lore_name = "Spell " + lore_name.replace(spell_ident, "").replace(possible_sep, "").strip()
    elif prayer_ident in lore_name:
        new_lore_name = "Prayer " + lore_name.replace(prayer_ident, "").replace(possible_sep, "").strip()
    elif manifestation_ident in lore_name:
        new_lore_name = "Manifestation " + lore_name.replace(manifestation_ident, "").replace(possible_sep, "").strip()
    else:
        new_lore_name = lore_name.strip()

    return new_lore_name


def replace_bullet_points(text: str, sep: str = " & ") -> str:
    """
    Removes bullet points and spaces if present to attach the modifiers of a unit
    :param text: The text in which to replace bullet points
    :param sep: The new separator with which to replace the bullet points (default: &)
    :return: The resulting text after replacement
    """
    bullet_point = chr(8226)
    pattern = rf"\s*{bullet_point}\s*"

    return re.sub(pattern, sep, text)


def insert_after(text: str, substring: str, to_insert: str) -> str:
    """
    Ensures there is a space after the given substring.
    If the substring is not present, return text as is.
    :param text: The text in which the substring is located
    :param substring: The substring after which to insert the space
    :param to_insert: The text to insert after the substring
    :return: text with space inserted
    """
    pattern = rf"{re.escape(substring)}\s*"
    replacement = f"{substring}{to_insert}"

    return re.sub(pattern, replacement, text)


def insert_before(text: str, substring: str, to_insert: str) -> str:
    """
    Ensures there is a space before the given substring.
    If the substring is not present, return text as is.
    :param text: The text in which the substring is located
    :param substring: The substring before which to insert the space
    :param to_insert: The text to insert before the substring
    :return: text with space inserted
    """
    pattern = rf"\s*{re.escape(substring)}"
    replacement = f"{to_insert}{substring}"

    return re.sub(pattern, replacement, text, count=1)
