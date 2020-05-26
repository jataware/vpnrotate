import aiohttp

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0",
    "connection": "keep-alive",
    "cache-control": "max-age=0",
    "accept": "*/*",
    "accept-language": "en-US;q=1.0,en;q=0.9",
}


async def getCountryCodes():
    url = "https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_countries"
    async with aiohttp.ClientSession(raise_for_status=True, headers=HEADERS) as session:
        async with session.get(url) as resp:
            jsonarray = await resp.json()
            return {item.get("code").lower(): item.get("id") for item in jsonarray}


async def getSecure():
    url = "https://api.nordvpn.com/vpn/check/full"
    async with aiohttp.ClientSession(raise_for_status=True, headers=HEADERS) as session:
        async with session.get(url) as resp:
            return await resp.json()


async def getRecommendations(country_code=None):
    def parse(o):
        return {
            "hostname": o.get("hostname"),
            "name": o.get("name"),
            "ip": o.get("station"),
            "load": o.get("load"),
        }

    url = "https://nordvpn.com/wp-admin/admin-ajax.php?action=servers_recommendations"
    if country_code:
        url += "&filters={%22country_id%22:" + str(country_code) + "}"
    async with aiohttp.ClientSession(raise_for_status=True, headers=HEADERS) as session:
        async with session.get(url) as resp:
            jsonarray = await resp.json()
            return [parse(o) for o in jsonarray]
