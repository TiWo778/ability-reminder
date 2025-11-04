from pathlib import Path

from src.constants import DEFAULT_BASE_DIR
from src.core.pdf_generator import generate_abilities_pdf
from src.core.services.list_service import ListService


class PDFService:
    """
    Interface for creating PDF files
    """
    def __init__(self, list_service: ListService):
        """
        Constructor
        :param list_service: list service holding the parsed army list
        """
        self.list_service = list_service
        self._pdf_dir: str | None = None

    def change_pdf_location(self, new_dir: str | Path):
        """
        Sets the location at which the PDF files are created
        :param new_dir: the new location of the PDF files
        """
        self._pdf_dir = new_dir

    def make_pdf(self):
        """
        Creates a PDF file for the army list held by the list_service
        :return: the path to the created PDF file
        """
        army_list = self.list_service.get_list()
        cleaned_list_name = army_list.name.replace("/", "-").replace("\\", "-").replace("|", "-")

        if not self._pdf_dir:
            self._pdf_dir = DEFAULT_BASE_DIR / "pdfs"

        out_dir_path = Path(self._pdf_dir)
        out_dir_path.mkdir(parents=True, exist_ok=True)

        out_file = out_dir_path / f"{cleaned_list_name}.pdf"
        generate_abilities_pdf(army_list, out_file)

        return out_file