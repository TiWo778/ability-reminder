from src.core.ability_timings import get_abilities_grouped_by_timing, get_abilities_grouped_w_o_any
from src.core.services.list_service import ListService


class AbilityService:
    """
    Interface for getting abilities grouped by timings.
    """
    def __init__(self, list_service: ListService):
        """
        Constructor.
        :param list_service: the list service which holds the army list
        """
        self.list_service = list_service

    def get_all_abilities_grouped_by_timing(self) -> dict[str, list]:
        """
        Gets all abilities grouped by their respective timings
        :return: dict containing timings as keys and lists of abilities as values
        """
        return get_abilities_grouped_by_timing(self.list_service.get_list())

    def get_abilities_grouped_by_phases(self) -> dict[str, list]:
        """
        Gets all abilities grouped by their respective timings with 'Any ...' timings merged into the respective phases
        :return: dict containing timings as keys and lists of abilities as values
        """
        return get_abilities_grouped_w_o_any(self.list_service.get_list())
