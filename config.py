import json
from paths import get_base_dir

CONFIG_PATH = get_base_dir() / "config.json"

DEFAULT_THEME = {
    "text": "#D9D9DA",
    "card_bg": "#797878",
    "border": "#FFFFFF",
    "divider": "#FFFFFF",
    "row_separator": "#EEEEEE",
    "xlsx_header_bg": "FFFFFF",
    "pdf_header_bg": "#DDDDDD",
    "save_fail": "#F20A0A",
    "save_success": "#48F20A",
}

DEFAULT_WINDOW = {
    "width": 1000,
    "height": 850,
    "min_width": 800,
    "min_height": 800,
}

DEFAULT_CONFIG = {
    "theme": DEFAULT_THEME,
    "window": DEFAULT_WINDOW,
}


def load_config():
    """
    Loads config.json, filling in any missing keys (or the whole file,
    if it's missing/unreadable) with defaults, so a partial or broken
    config file never crashes the app.
    """
    data = {}

    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            data = {}
    else:
        save_config(DEFAULT_CONFIG)
        data = DEFAULT_CONFIG

    theme = {**DEFAULT_THEME, **data.get("theme", {})}
    window = {**DEFAULT_WINDOW, **data.get("window", {})}

    return {"theme": theme, "window": window}


def save_config(config):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as file:
            json.dump(config, file, indent=2)
    except OSError:
        pass


CONFIG = load_config()
THEME = CONFIG["theme"]
WINDOW = CONFIG["window"]