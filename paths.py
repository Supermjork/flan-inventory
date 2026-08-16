import sys
from pathlib import Path


def get_base_dir():
    """
    Returns the directory data files (database, config) should live in.

    - When running as a normal Python script: the project folder.
    - When packaged with PyInstaller (--onefile or --onedir): the folder
      containing the actual .exe, NOT the temporary extraction folder
      (sys._MEIPASS), which is wiped after the app closes. This keeps a
      packaged app "portable" — its data sits right next to the .exe.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent

    return Path(__file__).parent