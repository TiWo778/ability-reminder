from src.classes import List
from src.core.list_parser import parse_list

class ListService:
    """
    Interface for parsing army lists
    """
    def __init__(self):
        self._army_list: List | None = None
        self._data_dir: str | None = None

    def change_data_dir(self, new_dir):
        """
        Sets the location of the data files
        :param new_dir: the location of the data files
        """
        self._data_dir = new_dir

    def load_from_text(self, text: str):
        """
        Parses an army list text to a list object from text directly
        :param text: the list text to parse
        """
        self._army_list = parse_list(text, self._data_dir)

    def load_from_file(self, filepath: str):
        """
        Parses an army list text to a list object from a file
        :param filepath: the path to the text file
        """
        with open(filepath, "r") as file:
            self._army_list = parse_list(file.read(), self._data_dir)

    def get_list(self):
        """
        Getter for the parsed army list
        :return: The List instance
        """
        if not self._army_list:
            raise RuntimeError("No List is loaded!")
        return self._army_list