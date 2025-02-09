"""Checks for upgrades for Waydroid images without restarting sessions.

This script is intended to be run as a normal user,
since it will not write anything to the system.

If an upgrade is available, it will be applied by calling "sudo waydroid upgrade".
You can override this behavior by setting the "NO_UPGRADE" environment variable.
"""

import asyncio
import logging
import os
import sys

import aiohttp

from tools import config


async def get_update_json(
    session: aiohttp.ClientSession,
    url: str,
    headers: dict | None = None,
) -> list[dict]:
    """Fetch JSON from a URL."""
    if headers is None:
        headers = {}
    logging.info('Checking "%s" for updates', url)
    async with session.get(url) as response:
        response.raise_for_status()
        logging.info('Got response from "%s", extracting JSON', url)
        return (await response.json())["response"]


async def async_main() -> int:
    """Async entry point for the script."""
    # Prepare required arguments

    cfg = config.load()
    images_path = cfg["waydroid"]["images_path"]

    if images_path in config.defaults["preinstalled_images_paths"]:
        logging.warning(
            "Upgrade refused because Waydroid loads pre-installed image: %s",
            images_path,
        )

        return -1

    system_ota_url = cfg["waydroid"]["system_ota"]
    vendor_ota_url = cfg["waydroid"]["vendor_ota"]

    async with aiohttp.ClientSession() as session:
        system_responses, vendor_responses = await asyncio.gather(
            get_update_json(session, system_ota_url),
            get_update_json(session, vendor_ota_url),
        )

        updates = 0

        system_datetime = system_responses[0]["datetime"]
        if system_datetime > int(cfg["waydroid"]["system_datetime"]):
            logging.info("System upgrade available: %s", system_datetime)
            updates += 1
        else:
            logging.info("System is up to date: %s", system_datetime)

        vendor_datetime = vendor_responses[0]["datetime"]
        if vendor_datetime > int(cfg["waydroid"]["vendor_datetime"]):
            logging.info("Vendor upgrade available: %s", vendor_datetime)
            updates += 1
        else:
            logging.info("Vendor is up to date: %s", vendor_datetime)

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
