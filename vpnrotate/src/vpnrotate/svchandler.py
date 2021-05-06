import asyncio
import stat

import aiofiles
from aiofiles import os

OVPN_LOCK = asyncio.Semaphore(1)


async def file_exists(p):
    try:
        return stat.S_ISREG((await os.stat(p)).st_mode)
    except FileNotFoundError:
        return False


async def dir_exists(p):
    try:
        return stat.S_ISDIR((await os.stat(p)).st_mode)
    except FileNotFoundError:
        return False


async def file_copy(src: str, dest: str, buff_size: int = 4096):
    async with aiofiles.open(dest, mode="wb") as outfile, aiofiles.open(
        src, "rb"
    ) as infile:
        while bs := await infile.read(buff_size):
            await outfile.write(bs)
        await outfile.flush()


async def changeVPNConfig(vpnconfigs: str, vpnconf: str, server: str) -> dict:

    provider = {}

    # NordVPN
    if "nord" in server:
        ovpn_file = f"{vpnconfigs}/nordvpn/ovpn_tcp/{server}.tcp.ovpn"
        provider = {
            "provider": "nordvpn",
            "server": server,
            "ovpn": ovpn_file,
        }

    # Wind
    elif "Wind" in server:
        ovpn_file = f"{vpnconfigs}/wind/ovpn_tcp/{server}.ovpn"
        provider = {
            "provider": "windscribe",
            "server": server,
            "ovpn": ovpn_file,
        }

    # PIA
    else:
        ovpn_file = f"{vpnconfigs}/pia/ovpn_tcp/{server}.ovpn"
        provider = {
            "provider": "pia",
            "server": server,
            "ovpn": ovpn_file,
        }

    async with OVPN_LOCK:
        if not await file_exists(ovpn_file):
            raise Exception(f"ovpn file not found {ovpn_file}")
        try:
            await os.remove(vpnconf)

        except FileNotFoundError:
            pass
        await file_copy(ovpn_file, vpnconf)

        try:
            await os.remove("/etc/ovpn/auth.conf")
        except FileNotFoundError:
            pass

        if "nord" in server:
            await file_copy("/etc/ovpn/nord.conf", "/etc/ovpn/auth.conf")
            provider["auth"] = "/etc/ovpn/nord.conf"
        elif "Wind" in server:
            await file_copy("/etc/ovpn/wind.conf", "/etc/ovpn/auth.conf")
            provider["auth"] = "/etc/ovpn/wind.conf"
        else:
            await file_copy("/etc/ovpn/pia.conf", "/etc/ovpn/auth.conf")
            provider["auth"] = "/etc/ovpn/pia.conf"

    return provider


async def restartVPN():
    async with OVPN_LOCK:
        process = await asyncio.create_subprocess_exec("sv", "restart", "ovpn")
        rc = await process.wait()
        return rc == 0, rc
