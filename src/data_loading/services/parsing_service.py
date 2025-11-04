from pathlib import Path

from src.constants import DEFAULT_BASE_DIR
from src.classes import Faction
from src.data_loading.faction_parser import parse_files_for_faction

class ParsingService:
    """
    Interface for Parsing data files into Faction objects.
    """
    def __init__(self):
        self._faction: str | None = None
        self._army_of_renown: str | None = None
        self._data_location: str | Path = Path(f"{DEFAULT_BASE_DIR}/data")

    def load_faction(self, faction: str):
        """
        Sets the faction name to parse later
        :param faction: the name of the faction
        """
        self._faction = faction

    def load_army_of_renown(self, army_of_renown: str):
        """
        Sets the army of renown name to parse later
        :param army_of_renown: the army of renown name
        """
        self._army_of_renown = army_of_renown

    def change_data_location(self, data_location: str | Path):
        """
        Sets the location of the data files to parse
        :param data_location: the location of the data files
        """
        self._data_location = Path(data_location)

    def get_faction(self) -> Faction:
        """
        Returns the parsed Faction object
        :return: Faction instance for the specified faction and army of renown
        """
        return parse_files_for_faction(self._faction, self._army_of_renown, self._data_location)