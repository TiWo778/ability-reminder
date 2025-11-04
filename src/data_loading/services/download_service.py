from pathlib import Path

from src.constants import DEFAULT_BASE_DIR
from src.data_loading.github_downloader import download_files_for_faction, download_all_faction_files, delete_all_faction_files, redownload_files

class DownloadService:
    """
    Interface for downloading data from GitHub repositories.
    """
    def __init__(self):
        self._download_dir: Path = Path(f"{DEFAULT_BASE_DIR}/data")

    def change_download_dir(self, download_dir: str | Path):
        """
        Sets the directory in which to download data.
        :param download_dir: The new directory.
        """
        self._download_dir = Path(download_dir)

    def refresh_all_files_present(self) -> list[Path]:
        """
        Re-download all files currently downloaded in download_dir.
        :return: List of paths to downloaded files.
        """
        return redownload_files(self._download_dir)

    def download_all_files(self) -> list[Path]:
        """
        Download all files available in the data repo.
        :return: List of paths to downloaded files.
        """
        return download_all_faction_files(self._download_dir)

    def download_faction_files(self, faction_name: str, aor_name: str | None=None) -> list[Path]:
        """
        Download files needed to parse a faction/army of renown.
        :param faction_name: The faction name for which to download files.
        :param aor_name: The name of the army of renown (Optional, defaults to None).
        :return: List of paths to downloaded files.
        """
        return download_files_for_faction(faction_name, aor_name, self._download_dir)

    def delete_all_files_present(self):
        """
        Delete all data files present in download_dir.
        """
        delete_all_faction_files(self._download_dir)