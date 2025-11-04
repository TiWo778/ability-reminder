import yaml
import sys
from pathlib import Path
import shutil
import os

class ConfigReader:
    """
    Config Reader Class
    """
    def __init__(self, config_path: str | Path | None = None):
        """
        Constructor
        :param config_path: Path to config file, if None will use default config path for the OS (Optional, defaults to None)
        """
        if config_path is None:
            self.config_path = self._get_persistent_config_path()
        else:
            self.config_path = Path(config_path)

        self.config = {}
        self._ensure_config_exists()
        self.read_config()

    def _get_persistent_config_path(self) -> Path:
        """
        Return a user-writable path for persistent settings.
        :return: Path to config file
        """
        if sys.platform == "win32":
            base_dir = Path(os.environ.get("APPDATA", Path.home())) / "AbilityReminders"
        else:
            base_dir = Path.home() / ".ability_reminders"
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir / "config.yaml"

    def _get_default_config_path(self) -> Path:
        """
        Return the path to the bundled default config.
        :return: Path to config file
        """
        if hasattr(sys, "_MEIPASS"):
            # PyInstaller: _MEIPASS is the temporary folder
            base_path = Path(sys._MEIPASS)
        else:
            # Development environment
            base_path = Path(__file__).parent
        return base_path / "configs" / "config.yaml"

    def _ensure_config_exists(self):
        """
        Copy default config if persistent config does not exist.
        """
        if not self.config_path.exists():
            default_config = self._get_default_config_path()
            shutil.copy(default_config, self.config_path)

    def read_config(self):
        """
        Load the config from the persistent file.
        """
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f) or {}

    def get_config(self):
        """
        Get the full config
        :return: Full config object
        """
        return self.config

    def get(self, field, default=None):
        """
        Gets a specific config value
        :param field: field to get
        :param default: default value to return if field is not found
        :return: value at the field
        """
        return self.config.get(field, default)

    def set(self, field, value):
        """
        Set a value and save immediately
        :param field: field to set
        :param value: value to set
        """
        self.config[field] = value
        self._save()

    def _save(self):
        """
        Helper to write the current config to disk.
        """
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(self.config, f, sort_keys=False, default_flow_style=False)
