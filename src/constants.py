import sys
from pathlib import Path
import os

DEFAULT_BASE_DIR = Path(os.environ.get("APPDATA", Path.home())) / "AbilityReminders" if sys.platform == "win32" else Path.home() / ".ability_reminders"
FONT_PATH = Path(sys._MEIPASS) / "fonts" if hasattr(sys, "_MEIPASS") else Path(__file__).parent.resolve() / "fonts"
