import logging
from pathlib import Path

from .constants import DEFAULT_BASE_DIR

packages = [
    "data_loading",
    "gui",
    "core"
]

Path(DEFAULT_BASE_DIR / "logs").mkdir(parents=True, exist_ok=True)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# File handlers per package
file_handlers = {}
for pkg_name in packages:
    fh = logging.FileHandler(f"{DEFAULT_BASE_DIR}/logs/{pkg_name}.log", encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    file_handlers[pkg_name] = fh


def get_logger_for_package(package_name: str):
    logger = logging.getLogger(package_name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Avoid adding multiple handlers if logger already exists
    if not logger.handlers:
        logger.addHandler(console_handler)

        if package_name in file_handlers:
            logger.addHandler(file_handlers[package_name])

    return logger
