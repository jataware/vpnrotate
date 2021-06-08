import datetime

import aiohttp


def fmt_now(pattern="%Y%m%d%H%M%S"):
    return datetime.datetime.utcnow().strftime(pattern)


def deep_get(d, path, default=None):
    """
    Take array or string as the path to a dict item and return the item or default if path does not exist.
    """
    if not d or not path:
        return d

    parts = path.split(".") if isinstance(path, str) else path
    return deep_get(d.get(parts[0]), parts[1:], default) if d.get(parts[0]) else default


HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
    "connection": "keep-alive",
    "cache-control": "max-age=0",
    "accept": "*/*",
    "accept-language": "en-US;q=1.0,en;q=0.9",
}


async def get_ip_info(ip_url, extended=False):
    async with aiohttp.ClientSession(raise_for_status=True, headers=HEADERS) as session:
        async with session.get(ip_url) as resp:
            ip = await resp.text()
            if not extended:
                return {"ip": ip}
        async with session.get(
            f"http://ipinfo.io/{ip}", headers={**HEADERS, "accept": "application/json"}
        ) as resp:
            return await resp.json()
