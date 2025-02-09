# waydroid-upgrade

This script checks for upgrades for Waydroid system and vendor images,
without restarting Waydroid sessions.

If an upgrade is available, it will be applied by calling "sudo waydroid upgrade".

## Usage

Install this as a CLI:

```shell
uv tool install git+https://github.com/Jisu-Woniu/waydroid-upgrade
# Alternatively, use pipx:
pipx install git+https://github.com/Jisu-Woniu/waydroid-upgrade
# Then invoke the CLI with:
waydroid-upgrade
```

Set environment variable `NO_UPGRADE` to skip the `sudo waydroid upgrade` invocation:

```shell
NO_UPGRADE=1 waydroid-upgrade
```

## Development

Clone this repository and install the dependencies. We use [uv](https://github.com/astral-sh/uv) for development:

```shell
git clone https://github.com/Jisu-Woniu/waydroid-upgrade.git
cd waydroid-upgrade
uv sync --locked
```
