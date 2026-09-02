"""Validated configuration loading and atomic saving for Foco."""

import copy
import json
from pathlib import Path


DEFAULT_CONFIG = {
    "focus_modes": {"deep_work": 90, "quick_focus": 25},
    "idle_timeout": 5,
    "pseudo_productive_limit": 10,
    "building_apps": ["code.exe", "idea64.exe", "pycharm64.exe", "cmd.exe",
                      "powershell.exe", "terminal.exe"],
    "studying_apps": ["canvas", "pdf", "notion", "onenote", "acrobat", "reader"],
    "applying_sites": ["linkedin.com", "indeed.com", "glassdoor.com", "jobs.com"],
    "pseudo_productive_sites": ["youtube.com", "reddit.com", "twitter.com",
                                "facebook.com", "instagram.com"],
    "blocked_sites": [
        "facebook.com", "www.facebook.com", "twitter.com", "www.twitter.com", "x.com",
        "www.x.com", "instagram.com", "www.instagram.com", "tiktok.com", "www.tiktok.com",
        "snapchat.com", "www.snapchat.com", "discord.com", "www.discord.com", "reddit.com",
        "www.reddit.com", "old.reddit.com", "new.reddit.com", "9gag.com", "www.9gag.com",
        "buzzfeed.com", "www.buzzfeed.com", "imgur.com", "www.imgur.com", "youtube.com",
        "www.youtube.com", "m.youtube.com", "steam.com", "store.steampowered.com", "twitch.tv",
        "www.twitch.tv", "www.epicgames.com", "cnn.com", "www.cnn.com", "bbc.com",
        "www.bbc.com", "news.ycombinator.com", "amazon.com", "www.amazon.com",
        "shopping.amazon.com", "ebay.com", "www.ebay.com", "aliexpress.com",
        "www.aliexpress.com"
    ],
    "blocked_apps": [
        "steam.exe", "steamwebhelper.exe", "epicgameslauncher.exe", "epicgames.exe",
        "origin.exe", "originwebhelperservice.exe", "battlenet.exe", "battle.net.exe",
        "riotclientservices.exe", "valorant.exe", "leagueoflegends.exe", "minecraft.exe",
        "minecraftlauncher.exe", "spotify.exe", "spotifywebhelper.exe", "netflix.exe",
        "hulu.exe", "disney+.exe", "vlc.exe", "mediaplayer.exe", "discord.exe",
        "slack.exe", "teams.exe", "whatsapp.exe", "telegram.exe", "torrent.exe",
        "utorrent.exe", "bittorrent.exe"
    ],
}

LIST_KEYS = {
    "building_apps", "studying_apps", "applying_sites", "pseudo_productive_sites",
    "blocked_sites", "blocked_apps",
}


def validate_config(config):
    validated = copy.deepcopy(DEFAULT_CONFIG)
    validated.update(config or {})

    modes = validated.get("focus_modes", {})
    validated["focus_modes"] = {
        "deep_work": max(1, int(modes.get("deep_work", 90))),
        "quick_focus": max(1, int(modes.get("quick_focus", 25))),
    }
    validated["idle_timeout"] = max(1, float(validated.get("idle_timeout", 5)))
    validated["pseudo_productive_limit"] = max(
        0, float(validated.get("pseudo_productive_limit", 10))
    )
    for key in LIST_KEYS:
        value = validated.get(key, [])
        if not isinstance(value, list):
            raise ValueError(f"{key} must be a list")
        validated[key] = list(dict.fromkeys(
            str(item).strip().lower() for item in value if str(item).strip()
        ))
    return validated


def load_config(path="config.json"):
    config_path = Path(path)
    if config_path.exists():
        try:
            return validate_config(json.loads(config_path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError, TypeError, ValueError) as error:
            print(f"Could not load configuration; using defaults: {error}")
    return validate_config({})


def save_config(config, path="config.json"):
    validated = validate_config(config)
    config_path = Path(path)
    temp_path = config_path.with_suffix('.tmp')
    temp_path.write_text(json.dumps(validated, indent=2) + "\n", encoding="utf-8")
    temp_path.replace(config_path)
    return validated
