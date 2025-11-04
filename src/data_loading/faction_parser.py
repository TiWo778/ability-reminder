from pathlib import Path
from lxml import etree

from .github_downloader import download_files_for_faction
from .constants import SEPARATOR, DATA_FILE_EXTENSION, UNIT_FILE_TOKEN, POSSIBLE_ENHANCEMENT_TYPES, POSSIBLE_LORE_TYPES, GENERAL_MANIFESTATION_LORES
from src.classes import Ability,Weapon,Unit,Faction

from src.constants import DEFAULT_BASE_DIR
from src.logging_config import get_logger_for_package

logger = get_logger_for_package(__package__.split('.')[-1])


def read_file(faction_name: str, aor_name: str | None=None, data_path: str | Path=f"{DEFAULT_BASE_DIR}/data") -> tuple[Path, Path, Path, Path]:
    """
    Reads the faction files for a given faction and army of renown and starts a download if necessary
    :param faction_name: the name of the faction
    :param aor_name: the name of the army of renown (Optional, defaults to None)
    :param data_path: the path of the data files (Optional, defaults to src/data)
    :return: the paths to the faction file, unit file, army of renown file and spell/prayer/manifestation lore file
    """
    spells_file = Path(f"{data_path}/Lores{DATA_FILE_EXTENSION}")
    faction_file = Path(f"{data_path}/{faction_name}{DATA_FILE_EXTENSION}")
    unit_file = Path(f"{data_path}/{faction_name}{SEPARATOR}{UNIT_FILE_TOKEN}{DATA_FILE_EXTENSION}")
    aor_file = Path(f"{data_path}/{faction_name}{SEPARATOR}{aor_name}{DATA_FILE_EXTENSION}") if aor_name else None
    file_missing = False

    # Check if the files are already downloaded and download them if necessary
    if not faction_file.is_file() or not unit_file.is_file() or not spells_file.is_file():
        file_missing = True

    # Some Armies of Renown have different names in the official App than the dataset (The Knights of New Summercourt vs New Summercourt)
    if aor_name is not None and not aor_file.is_file():
        found_aor_file = False

        for file in Path(data_path).iterdir():
            if file.is_file():
                alt_aor_file_ident = file.name.split(".")[0].split(SEPARATOR)[-1].strip()
                if not alt_aor_file_ident in aor_name:
                    continue
                else:
                    aor_file = file
                    found_aor_file = True
                    break

        file_missing = not found_aor_file

    if file_missing:
        logger.debug("Found missing files for %s - %s missing", faction_name, aor_name)
        filepaths = download_files_for_faction(faction_name, aor_name, data_path)

        # Assign downloaded files to the appropriate variables
        for file in filepaths:
            filepath = Path(file)

            if filepath.name.split(SEPARATOR)[-1].removesuffix(DATA_FILE_EXTENSION) in UNIT_FILE_TOKEN:
                unit_file = filepath
            elif aor_name is not None and filepath.name.split(SEPARATOR)[-1].removesuffix(DATA_FILE_EXTENSION) in aor_name:
                aor_file = filepath
            elif filepath.name.split(SEPARATOR)[-1].removesuffix(DATA_FILE_EXTENSION) in faction_name:
                faction_file = filepath
            elif filepath == spells_file:
                spells_file = filepath

    return faction_file, unit_file, aor_file, spells_file


def parse_files_for_faction(faction_name: str, aor_name: str | None=None, data_path: str | Path=f"{DEFAULT_BASE_DIR}/data") -> Faction:
    """
    Reads and parses the files for a given faction and army of renown to a faction object
    :param faction_name: name of the faction
    :param aor_name: name of the army of renown (Optional, defaults to None)
    :param data_path: the path of the data files (Optional, defaults to src/data)
    :return: a faction object representing the faction and army of renown
    """
    faction_file, unit_file, aor_file, spells_file = read_file(faction_name, aor_name, data_path)

    # declare namespace and parse files
    ns = {'bs': 'http://www.battlescribe.net/schema/catalogueSchema'}

    logger.debug("Parsing files for faction %s - %s", faction_name, aor_name)

    if aor_file is not None:
        faction_data = parse_faction(aor_file, spells_file, ns)
    else:
        faction_data = parse_faction(faction_file, spells_file, ns)

    battle_traits, battle_formations, enhancements, lores = faction_data
    units = parse_units(unit_file, ns)
    faction = Faction(
        faction_name,
        battle_traits,
        battle_formations,
        enhancements,
        lores,
        units
    )

    logger.debug("Finished parsing faction data for %s - %s", faction_name, aor_name)

    return faction


def parse_faction(faction_file:Path, spells_file:Path, ns: dict[str, str]) -> tuple[list[Ability],  dict[str, Ability],  dict[str, list[Ability]], dict[str, list[Ability]]]:
    """
    Parses faction wide abilities based on the .cat files relevant for a faction
    :param faction_file: the .cat file containing the faction data
    :param spells_file: the .cat file containing the spell/prayer/manifestation lore data
    :param ns: the namespace to use
    :return: tuple containing battle traits, battle formations, enhancements, spell/prayer/manifestation lores
    """
    faction_tree = etree.parse(str(faction_file))
    faction_root = faction_tree.getroot()
    spells_tree = etree.parse(str(spells_file))
    spells_root = spells_tree.getroot()

    # find relevant fields for battle traits, battle formations, and enhancements
    shared_sel_entries = faction_root.find("bs:sharedSelectionEntries", namespaces=ns)
    shared_profiles = faction_root.find("bs:sharedProfiles", namespaces=ns)
    shared_sel_entry_groups = faction_root.find("bs:sharedSelectionEntryGroups", namespaces=ns)
    spells_shared_sel_entry_groups = spells_root.find("bs:sharedSelectionEntryGroups", namespaces=ns)

    battle_traits = get_battle_traits(shared_sel_entries, shared_profiles, ns)
    battle_formations = get_battle_formations(shared_sel_entry_groups, ns)
    enhancements = get_enhancements(shared_sel_entry_groups, ns)
    lores = get_lores(shared_sel_entry_groups, spells_shared_sel_entry_groups, ns)

    return battle_traits, battle_formations, enhancements, lores


def get_battle_traits(shared_sel_entries, shared_profiles, ns: dict[str, str]) -> list[Ability]:
    """
    Get the available battle traits based on the shared selection entries and shared profiles.
    :param shared_sel_entries: the xml shared selection entries
    :param shared_profiles: the xml shared profiles
    :param ns: the namespace to use
    :return: list of abilities
    """
    battle_trait_entry = shared_sel_entries.xpath("./bs:selectionEntry[contains(@name, 'Battle Traits')]", namespaces=ns)[0]
    if battle_trait_entry is None:
        logger.warning("No Battle Traits found in faction file.")
        return []

    profiles = battle_trait_entry.find("bs:profiles", namespaces=ns)
    # Some armies (e.g. Flesh-eater Courts) have additional battle traits in the shared Profile section
    if shared_profiles is not None:
        profiles.extend(shared_profiles.findall("bs:profile", namespaces=ns))

    battle_traits = [build_ability_from_profile(profile, ns) for profile in profiles]

    logger.debug("Finished parsing battle traits")

    return battle_traits


def get_battle_formations(shared_sel_entry_groups, ns: dict[str, str]) -> dict[str, Ability]:
    """
    Get the battle formations available based on the shared selection entry groups.
    :param shared_sel_entry_groups: the xml shared selection entry groups
    :param ns: the namespace to use
    :return: dict containing battle formation name as key and granted ability as value
    """
    battle_formation_entries = shared_sel_entry_groups.xpath("./bs:selectionEntryGroup[contains(@name, 'Battle Formations')]", namespaces=ns)
    if not battle_formation_entries:
        return {}
    else:
        battle_formation_entry = battle_formation_entries[0]

    if battle_formation_entry is None:
        return {}

    battle_formations = {}
    formations = battle_formation_entry.find("bs:selectionEntries", namespaces=ns)
    for formation in formations:
        formation_name = formation.get("name")
        profile = formation.find("bs:profiles", namespaces=ns)[0]
        battle_formations[formation_name] = build_ability_from_profile(profile, ns)

    logger.debug("Finished parsing battle formations")

    return battle_formations


def get_enhancements(shared_sel_entry_groups, ns: dict[str, str]) -> dict[str, list[Ability]]:
    """
    Get the enhancements available based on the shared selection entry groups
    :param shared_sel_entry_groups: the xml shared selection entry groups
    :param ns: the namespace to use
    :return: a dict containing enhancement table names as keys and a list of the enhancements in those table as values
    """
    enhancement_entry_groups = []

    for keyword in POSSIBLE_ENHANCEMENT_TYPES:
        xpath = f"./bs:selectionEntryGroup[contains(@name, '{keyword}')]"
        enhancement_entry_groups.extend(shared_sel_entry_groups.xpath(xpath, namespaces=ns))

    enhancements = {}
    for enhancement_type in enhancement_entry_groups:
        groups = enhancement_type.findall(".//bs:selectionEntryGroups/bs:selectionEntryGroup", namespaces=ns)

        for group in groups:
            group_name = group.get("name")
            enhancements[group_name] = []
            profiles = group.findall(".//bs:selectionEntries/bs:selectionEntry/bs:profiles/bs:profile", namespaces=ns)

            for profile in profiles:
                enhancements[group_name].append(build_ability_from_profile(profile, ns))

    return enhancements


def get_lores(shared_sel_entry_groups, spells_shared_sel_entry_groups, ns: dict[str, str]) -> dict[str, list[Ability]]:
    """
    Get spell, prayer, and manifestation lores from shared selection entry groups.
    :param shared_sel_entry_groups: the xml shared selection entry groups in which lore names are available
    :param spells_shared_sel_entry_groups: the xml shared selection entry groups in which lore abilities are available
    :param ns: the namespace to use
    :return: dict containing lore names as keys and list of spell/prayer abilities as values
    """
    lore_entry_groups = []

    for keyword in POSSIBLE_LORE_TYPES:
        xpath = f"./bs:selectionEntryGroup[contains(@name, '{keyword}')]"
        lore_entry_groups.extend(shared_sel_entry_groups.xpath(xpath, namespaces=ns))

    # Find available lores in faction file and add universal ones
    lores = {
        lore.get("name"): []
        for lore_type in lore_entry_groups
        for lore in lore_type.findall(".//bs:selectionEntries/bs:selectionEntry", namespaces=ns)
    }
    lores.update({key: [] for key in GENERAL_MANIFESTATION_LORES if key not in lores})

    # Find corresponding lores in Lores.cat file and add them to the dict
    for lore in lores:
        xpath = f'./bs:selectionEntryGroup[contains(@name, "{lore}")]'
        spell_group = spells_shared_sel_entry_groups.xpath(xpath, namespaces=ns)[0]
        profiles = spell_group.findall(".//bs:selectionEntries/bs:selectionEntry/bs:profiles/bs:profile", namespaces=ns)
        for profile in profiles:
            lores[lore].append(build_ability_from_profile(profile, ns))

    logger.debug("Finished parsing lores")

    return lores


def parse_units(unit_file: Path, ns: dict[str, str]) -> list[Unit]:
    """
    Parse a .cat (xml) file containing unit data.
    :param unit_file: path to the .cat file
    :param ns: the namespace to use
    :return: units present in the .cat file
    """
    unit_tree = etree.parse(unit_file)
    unit_root = unit_tree.getroot()

    shared_sel_entries = unit_root.find("bs:sharedSelectionEntries", namespaces=ns)
    shared_profiles = unit_root.find("bs:sharedProfiles", namespaces=ns)

    units = get_units(shared_sel_entries, shared_profiles, ns)

    logger.debug("Finished parsing units")

    return units


def get_units(shared_sel_entries, shared_profiles, ns: dict[str, str]) -> list[Unit]:
    """
    Get unit objects from shared selection entries and shared profiles
    :param shared_sel_entries: xml shared selection entries
    :param shared_profiles: xml shared profiles
    :param ns: the namespace to use
    :return: list of units
    """
    units = []
    keyword_separator = ","
    unit_identifier = "Unit"
    manifestation_identifier = "Manifestation"
    ability_identifier = "Ability"

    for entry in shared_sel_entries:
        unit_keywords = keyword_separator.join([link.get("name") for link in entry.find("bs:categoryLinks", namespaces=ns)])
        profiles = entry.findall("bs:profiles/bs:profile", namespaces=ns)

        # Store parts of a unit in a dict for later object creation
        unit_components = {"abilities": []}
        # Get information about unit characteristics and abilities
        for profile in profiles:

            if ability_identifier in profile.get("typeName"):
                unit_components["abilities"].append(build_ability_from_profile(profile, ns))

            elif any(s in profile.get("typeName") for s in [unit_identifier, manifestation_identifier]):
                characteristics = get_characteristics_dict(profile, ns)
                unit_components["name"] = entry.get("name")
                unit_components["move"] = characteristics.get("Move")
                unit_components["health"] = characteristics.get("Health")
                unit_components["save"] = characteristics.get("Save")
                unit_components["control"] = characteristics.get("Control")
                unit_components["banishment"] = characteristics.get("Banishment")

            else:
                continue

        # Some units (i.e. Skaven weapons teams have shared rules which are not directly found in their profile)
        if (info_link := entry.find("bs:infoLinks/bs:infoLink", namespaces=ns)) is not None:
            ability_cross_name = info_link.get("name")

            # Some universal abilities like "Beast" cannot be found in faction file. They will be ignored.
            ability_profile = shared_profiles.xpath(f"bs:profile[@name = '{ability_cross_name}']", namespaces=ns)
            if ability_profile:
                unit_components["abilities"].append(build_ability_from_profile(ability_profile[0], ns))

        # Get information about weapons
        weapons, additional_abilities = get_weapon_profiles(entry, ns)
        unit_components["abilities"].extend(additional_abilities)

        units.append(Unit(
            unit_components["name"],
            unit_components["move"],
            unit_components["health"],
            unit_components["control"],
            unit_components["banishment"],
            unit_components["save"],
            unit_keywords,
            weapons,
            unit_components["abilities"]
        ))

    return units


def get_weapon_profiles(unit_entry, ns: dict[str, str]) -> tuple[list[Weapon], list[Ability]]:
    """
    Gets the available weapon profiles for a given unit entry along with any special abilities granted by those weapons.
    :param unit_entry: xml unit entry
    :param ns: the namespace to use
    :return: list of weapon profiles and list of abilities
    """
    weapons = []
    additional_abilities = []

    # Check if the unit has weapon profiles
    if (top_sel_entries := unit_entry.findall("bs:selectionEntries/bs:selectionEntry", namespaces=ns)) is None:
        return [], []

    for entry_group in top_sel_entries:
        # If we don't have options, parse directly
        if not (options := entry_group.findall("bs:selectionEntryGroups/bs:selectionEntryGroup/bs:selectionEntries/bs:selectionEntry", namespaces=ns)):
            options = [entry_group]

        for option in options:
            # Get abilities the unit gets if equipped with that weapon
            if (profile := option.find("bs:profiles/bs:profile", namespaces=ns)) is not None:
                additional_abilities.append(build_ability_from_profile(profile, ns))

            weapons_available = option.findall("bs:selectionEntries/bs:selectionEntry", namespaces=ns)
            for weapon in weapons_available:
                weapon_profile = weapon.find("bs:profiles/bs:profile", namespaces=ns)
                characteristics = get_characteristics_dict(weapon_profile, ns)
                weapons.append(Weapon(
                    weapon_profile.get("name"),
                    weapon_profile.get("typeName"),
                    characteristics.get("Rng"),
                    characteristics.get("Atk"),
                    characteristics.get("Hit"),
                    characteristics.get("Wnd"),
                    characteristics.get("Rnd"),
                    characteristics.get("Dmg"),
                    characteristics.get("Ability"),
                ))

    # Remove duplicates
    weapons = list(set(weapons))

    return weapons, additional_abilities

def get_characteristics_dict(profile_element, namespace):
    """
    Helper method for reading characteristics in an ability from the XML tree
    :param profile_element: the profile of which to read the characteristics
    :param namespace: the namespace to use
    :return: a dictionary of characteristics with names as keys
    """
    chars = profile_element.xpath(
        "./bs:characteristics/bs:characteristic",
        namespaces=namespace
    )
    return {c.get("name"): c.text for c in chars}


def build_ability_from_profile(profile, ns: dict[str, str], cost_key=None) -> Ability:
    """
    Build an Ability object from a profile
    :param profile: the profile from which to build the ability
    :param ns: the namespace to use
    :param cost_key: they key to use for the cost field (None to find it automatically)
    :return: an Ability object
    """
    characteristics = get_characteristics_dict(profile, ns)
    if cost_key is None:
        cost_key = get_cost_key(characteristics)
    return Ability(
        profile.get("name"),
        profile.get("typeName"),
        characteristics.get("Timing"),
        characteristics.get("Keywords"),
        characteristics.get("Declare"),
        characteristics.get("Effect"),
        characteristics.get(cost_key)
    )


def get_cost_key(characteristics: dict[str,str]) -> str:
    """
    Finds the appropriate cost key for the given characteristics
    :param characteristics: dict containing the characteristics of an ability
    :return: cost key to use
    """
    valid_keys_for_cost_field = ["Cost", "Casting Value", "Chanting Value"]

    found_cost_candidates = (set(valid_keys_for_cost_field) & characteristics.keys())
    cost_key = next(iter(found_cost_candidates)) if found_cost_candidates else None

    return cost_key
