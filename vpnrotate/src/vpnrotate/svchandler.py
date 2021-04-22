import asyncio
import stat
import json
import subprocess

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
        # fmt: off
        while (bs := await infile.read(buff_size)):
            await outfile.write(bs)
        await outfile.flush()
        # fmt: on


async def changeVPNConfig(vpnconfigs: str, vpnconf: str, server: str):
    
    provider_info = f"{vpnconfigs}/local_connect/provider.txt"

    # NordVPN
    if "nord" in server:
        ovpn_file = f"{vpnconfigs}/nordvpn/ovpn_tcp/{server}.tcp.ovpn"
        provider(provider_info, "nordvpn", server)
    # Wind
    elif "Wind" in server:
        ovpn_file = f"{vpnconfigs}/wind/ovpn_tcp/{server}.ovpn"
        provider(provider_info, "windscribe", server)
    # PIA
    else:
        ovpn_file = f"{vpnconfigs}/pia/ovpn_tcp/{server}.ovpn"
        provider(provider_info, "pia", server)
        
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
        elif "Wind" in server:
            await file_copy("/etc/ovpn/wind.conf", "/etc/ovpn/auth.conf")
        else:
            await file_copy("/etc/ovpn/pia.conf", "/etc/ovpn/auth.conf")


async def restartVPN():
    async with OVPN_LOCK:
        process = await asyncio.create_subprocess_exec("sv", "restart", "ovpn")
        rc = await process.wait()
        return rc == 0, rc


def is_secure(fdir):
    try:
        with open(fdir) as f:
            local_info = json.load(f)

        # Get container IP information
        cmd = "curl -s ipinfo.io/$(curl -s ifconfig.me)"
        vpn_info = curlit(cmd)

        local_IP = local_info["ip"]
        container_IP = vpn_info["ip"]

        if local_IP != container_IP:
            secure = True
        else:
            secure = False

        content = {"secure": secure, "local_IP": local_IP, "container_IP": container_IP}

        return content
    except Exception as e:
        print(str(e))


def provider(fn, vpn, server):
    data = {}
    data["provider"] = vpn
    data["server"] = server
    
    with open(fn, 'w') as outfile:
        json.dump(data, outfile)


def curlit(cmd):
    output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    vpn_bytes, err = output.communicate()
    
    return json.loads(vpn_bytes.decode('utf8'))        
