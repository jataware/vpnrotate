import asyncio
import logging
import tempfile
from logging import Logger
from shutil import unpack_archive

import aiofiles
import aiohttp
from pathlib3x import Path

from . import config

logger: Logger = logging.getLogger(__name__)

CHUNK_SIZE = 1028

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
    "connection": "keep-alive",
    "cache-control": "max-age=0",
    "accept": "*/*",
    "accept-language": "en-US;q=1.0,en;q=0.9",
}


def remove_ovpn_configs(vpn_configs_dir):
    for path in Path(vpn_configs_dir).iterdir():
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            path.rmtree(ignore_errors=True)


async def getsave(session, outfile, url):
    async with aiofiles.open(outfile, mode="wb") as f:
        async with session.get(url) as response:
            while True:
                chunk = await response.content.read(CHUNK_SIZE)
                if not chunk:
                    break
                await f.write(chunk)


async def configure_nord(vpn_configs_dir):

    path = Path(f"{vpn_configs_dir}/nordvpn")
    path.mkdir(parents=True, exist_ok=True)

    tmpdir = tempfile.gettempdir()
    url = "https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip"

    tmpfile = f"{tmpdir}/nordvpn.zip"
    async with aiohttp.ClientSession(raise_for_status=True, headers=HEADERS) as session:
        await getsave(session, tmpfile, url)

    unpack_archive(tmpfile, path, "zip")


async def configure_pia(vpn_configs_dir):
    path = Path(f"{vpn_configs_dir}/pia/ovpn_tcp")
    path.mkdir(parents=True, exist_ok=True)

    tmpdir = tempfile.gettempdir()
    url = "https://www.privateinternetaccess.com/openvpn/openvpn.zip"

    tmpfile = f"{tmpdir}/pia.zip"
    async with aiohttp.ClientSession(raise_for_status=True, headers=HEADERS) as session:
        await getsave(session, tmpfile, url)

    unpack_archive(tmpfile, path, "zip")


async def configure_wind(vpn_configs_dir):
    path = Path(f"{vpn_configs_dir}/wind")
    path.mkdir(parents=True, exist_ok=True)

    tmpdir = tempfile.gettempdir()
    url = "https://vpnrotate.s3.amazonaws.com/ovpn_tcp.zip"

    tmpfile = f"{tmpdir}/wind.zip"

    async with aiohttp.ClientSession(raise_for_status=True, headers=HEADERS) as session:
        await getsave(session, tmpfile, url)

    unpack_archive(tmpfile, path, "zip")


async def run_ovpn_setup(settings, clean=True):

    vpn_configs_dir = settings["vpn_env"]["vpnconfigs"]
    logger.debug(f"vpn_configs_dir = {vpn_configs_dir}")

    if clean:
        logger.info(f"Removing contents of {vpn_configs_dir}")
        remove_ovpn_configs(vpn_configs_dir)

    if not Path(vpn_configs_dir).exists():
        raise Exception(f"vpn config base directory does not exist {vpn_configs_dir}")

    logger.info("Setting up Nord OVPN directory")
    await configure_nord(vpn_configs_dir)

    logger.info("Setting up PIA OVPN directory")
    await configure_pia(vpn_configs_dir)

    logger.info("Setting up Wind OVPN directory")
    await configure_wind(vpn_configs_dir)


def main() -> None:
    settings = config.get_config()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_ovpn_setup(settings))


if __name__ == "__main__":
    main()
