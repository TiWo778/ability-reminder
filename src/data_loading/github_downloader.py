import requests
from pathlib import Path
import json
from datetime import datetime, timedelta

from src.constants import DEFAULT_BASE_DIR
from src.logging_config import get_logger_for_package
from .constants import DATA_FILE_EXTENSION, SEPARATOR, UNIT_FILE_TOKEN, REPO_API_URL, RAW_BASE

logger = get_logger_for_package(__package__.split('.')[-1])


def get_repo_files(force_refresh=False, cache_file_location: str | Path=f"{DEFAULT_BASE_DIR}/data") -> list[str]:
    """
    Returns a list of .cat filenames in the BSData repo.
    Uses a cached version unless force_refresh=True or cache >24h old.
    :param force_refresh: whether to force refreshing the cache file or not
    :param cache_file_location: path to cache file (Optional, defaults to ROOT/data)
    :return: list of filenames for the .cat files found in the repo
    """
    cache_file = Path(cache_file_location) / "repo_cache.json"
    if cache_file.exists() and not force_refresh:
        mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        if datetime.now() - mtime < timedelta(hours=24):
            logger.info("Using cached file list from %s", str(cache_file))
            return json.load(open(cache_file))

    logger.info("Fetching file list from GitHub API...")
    response = requests.get(REPO_API_URL)
    if response.status_code != 200:
        logger.critical(
            "Failed to fetch repo contents: %s %s", response.status_code, response.text
        )
        raise SystemExit(1)

    files = response.json()
    cat_files = [f["name"] for f in files if f["type"] == "file" and f["name"].endswith(DATA_FILE_EXTENSION)]

    cache_file.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_file, "w") as cache_file:
        json.dump(cat_files, cache_file)
    logger.info("Cached %d file names to %s", len(cat_files), str(cache_file))

    return cat_files


def download_files(files: list[str], download_location: str | Path = f"{DEFAULT_BASE_DIR}/data") -> list[Path]:
    """
    Downloads files directly from raw.githubusercontent.com.
    :param files: list of filenames to download
    :param download_location: directory to download files to (Optional, defaults to src/data)
    :return: list of filepaths to downloaded files
    """
    download_location = Path(download_location)
    filepaths = []

    for file in files:
        url = f"{RAW_BASE}/{file}"
        path = download_location / file
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            logger.info("Downloading %s ...", url)
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with path.open("wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            filepaths.append(path)
            logger.info("Downloaded %s successfully.", file)
        except requests.exceptions.RequestException as e:
            logger.error("Failed to download %s: %s", file, e)

    return filepaths


def redownload_files(download_location: str | Path = f"{DEFAULT_BASE_DIR}/data"):
    """
    Re-downloads all files present in the given location.
    :param download_location: directory in which the files to re-download are located. (Optional, defaults to src/data)
    :return: list of filepaths of the re-downloaded files.
    """
    to_download = []

    for file in Path(download_location).iterdir():
        if file.is_file() and file.name.endswith(DATA_FILE_EXTENSION):
            to_download.append(file.name)

    return download_files(to_download, download_location)


def download_files_for_faction(faction_name: str, aor_name: str | None=None, download_location: str | Path=f"{DEFAULT_BASE_DIR}/data") -> list[Path]:
    """
    Downloads all files for a given faction and army of renown to the given location.
    :param faction_name: name of the faction to download.
    :param aor_name: name of the AOR to download. (Optional, defaults to None)
    :param download_location: directory to download the files to. (Optional, defaults to src/data)
    :return: filepaths of the downloaded files.
    """
    files = get_repo_files(cache_file_location=download_location)

    # Find files that match the given params
    matching_files = []
    for file in files:
        if not file.endswith(DATA_FILE_EXTENSION):
            continue

        parts = file.removesuffix(DATA_FILE_EXTENSION).split(SEPARATOR)
        file_faction = parts[0].strip()
        file_aor = parts[1].strip() if len(parts) > 1 else ""

        if faction_name not in file_faction:
            continue

        if aor_name is None and file_aor not in ["", UNIT_FILE_TOKEN]:
            continue

        if aor_name is not None and file_aor not in ["", UNIT_FILE_TOKEN] and file_aor not in aor_name:
            continue

        matching_files.append(file)

    if matching_files:
        matching_files.append("Lores.cat")

    logger.debug("Found %d files for %s: %s", len(matching_files), faction_name, ", ".join(matching_files))

    return download_files(matching_files, download_location)


def download_all_faction_files(download_location: str | Path = f"{DEFAULT_BASE_DIR}/data"):
    """
    Downloads all available faction files.
    :param download_location: directory to download the files to. (Optional, defaults to src/data)
    """
    files = get_repo_files(force_refresh=True, cache_file_location=download_location)
    return download_files(files, download_location)


def delete_all_faction_files(data_location: str | Path = f"{DEFAULT_BASE_DIR}/data"):
    """
    Deletes all available faction files.
    :param data_location: directory in which the files to delete are located. (Optional, defaults to src/data)
    """
    for file in Path(data_location).iterdir():
        if file.is_file() and file.name.endswith(DATA_FILE_EXTENSION):
            file.unlink()
            logger.info("Deleted file %s", file)