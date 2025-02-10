# Copyright 2021 Oliver Smith
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Waydroid configuration loader.

Derived from https://github.com/waydroid/waydroid/tree/7b31f7188a382ead687d291e5a168895efcc6747/tools/config,
and removed unused imports and dependencies.
"""

import configparser
from pathlib import Path

config_keys = [
    "system_datetime",
    "vendor_datetime",
]

defaults = {
    "work": "/var/lib/waydroid",
    "system_datetime": "0",
    "vendor_datetime": "0",
    "preinstalled_images_paths": [
        "/etc/waydroid-extra/images",
        "/usr/share/waydroid-extra/images",
    ],
}
defaults["images_path"] = defaults["work"] + "/images"


def load() -> configparser.ConfigParser:
    """Load the Waydroid configuration."""
    config = "/var/lib/waydroid/waydroid.cfg"

    cfg = configparser.ConfigParser()

    if Path(config).is_file():
        cfg.read(config)

    if "waydroid" not in cfg:
        cfg["waydroid"] = {}

    for key in defaults.items():
        if key in config_keys and key not in cfg["waydroid"]:
            cfg["waydroid"][key] = str(defaults[key])

    return cfg
