"""
Checks for upgrades for Waydroid images without restarting sessions.

This script is intended to be run as a normal user,
since it will not write anything to the system.

If an upgrade is available, it will call "sudo waydroid upgrade" to apply that.
You can skip that by setting the "NO_UPGRADE" environment variable.
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys

import aiohttp

from .tools import config


type JsonValues = (
    None | bool | float | int | str | list[JsonValues] | dict[str, JsonValues]
)


async def get_update_json(
    session: aiohttp.ClientSession,
    url: str,
) -> list[dict[str, JsonValues]]:
    """Fetch Waydroid update JSON from a URL."""
    logging.info('Checking "%s" for updates', url)
    async with session.get(url) as response:
        response.raise_for_status()
        logging.info('Got response from "%s", extracting JSON', url)
        return (await response.json())["response"]


async def async_main() -> int:
    """Async entry point for the script."""
    cfg = config.load()
    waydroid_config = cfg["waydroid"]
    images_path = waydroid_config["images_path"]

    if images_path in config.defaults["preinstalled_images_paths"]:
        logging.warning(
            "Upgrade refused because Waydroid loads pre-installed image: %s",
            images_path,
        )

        return 0

    system_ota_url = waydroid_config["system_ota"]
    vendor_ota_url = waydroid_config["vendor_ota"]

    async with aiohttp.ClientSession() as session:
        system_responses, vendor_responses = await asyncio.gather(
            get_update_json(session, system_ota_url),
            get_update_json(session, vendor_ota_url),
        )

        logging.info("Extraction completed.")

        updates = 0

        system_datetime = system_responses[0]["datetime"]
        assert isinstance(system_datetime, int)

        local_system_datetime = int(waydroid_config["system_datetime"])
        if system_datetime > local_system_datetime:
            logging.info("System upgrade available: %s", system_datetime)
            updates += 1
        else:
            logging.info("System is up to date: %s", local_system_datetime)

        vendor_datetime = vendor_responses[0]["datetime"]
        assert isinstance(vendor_datetime, int)

        local_vendor_datetime = int(waydroid_config["vendor_datetime"])
        if vendor_datetime > local_vendor_datetime:
            logging.info("Vendor upgrade available: %s", vendor_datetime)
            updates += 1
        else:
            logging.info("Vendor is up to date: %s", local_vendor_datetime)

        if updates != 0:
            if os.environ.get("NO_UPGRADE"):
                logging.info("%d upgrades available.", updates)
                return updates
            logging.info("Upgrades will be applied in 3 seconds.")
            await asyncio.sleep(3)

            process = await asyncio.subprocess.create_subprocess_exec(
                "sudo",
                "waydroid",
                "upgrade",
            )

            return await process.wait()

        return 0


def main() -> int:
    """Entry point for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format="[{asctime}.{msecs:03.0f} {levelname}] {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    return asyncio.run(async_main())


if __name__ == "__main__":
    sys.exit(main())
