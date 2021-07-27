import argparse
import asyncio
import json
import logging
import logging.config
from logging import Logger
from zipfile import ZipFile

import aiofiles
import aiohttp
from bs4 import BeautifulSoup

logger: Logger = logging.getLogger(__name__)

CHUNK_SIZE = 1028


async def postzip(sem, session, zipfile, filename, url, data):
    async with sem:
        logger.debug("file=%s, data=%s", filename, data)
        async with session.post(url, data=data) as response:
            text = await response.text()
            zipfile.writestr(filename, text)
        await asyncio.sleep(2)


async def login(session, user, password):
    async with session.post("https://res.windscribe.com/res/logintoken") as r:
        j = json.loads(await r.text())
        csrf_time = j["csrf_time"]
        csrf_token = j["csrf_token"]

    await asyncio.sleep(2)

    url = "https://windscribe.com/login"

    data = {
        "login": 1,
        "upgrade": 0,
        "username": user,
        "password": password,
        "csrf_time": csrf_time,
        "csrf_token": csrf_token,
        "code": "",
    }

    async with session.post(url, data=data):
        logger.info("Logged in")


def normalize_name(s):
    return f"Windscribe-{s.replace(' ', '')}"


async def get_config_locations(session):
    async with session.get("https://windscribe.com/getconfig/openvpn") as r:
        html = await r.text()
        soup = BeautifulSoup(html, "html.parser")
        xs = {
            normalize_name(opt.string): opt.attrs["value"]
            for opt in soup.find(id="location").find("optgroup").find_all("option")
        }
        return xs


async def get_credentials(session):
    url = "https://windscribe.com/getconfig/credentials?device=null&ip=null"
    async with session.get(url) as r:
        j = json.loads(await r.text())
        async with aiofiles.open("wind-creds.txt", mode="w") as f:
            await f.write(f"{j['username']}\n{j['password']}")


async def download(args):
    sem = asyncio.Semaphore(1)
    url = "https://windscribe.com/getconfig/openvpn"

    async with aiohttp.ClientSession(raise_for_status=True) as session:
        await login(session, args.user, args.password)
        config_locations = await get_config_locations(session)
        data = {"protocol": "tcp", "port": "443", "version": "3b"}

        if args.z:
            with ZipFile("ovpn_tcp.zip", "w") as z:
                tasks = [
                    postzip(
                        sem,
                        session,
                        z,
                        f"ovpn_tcp/{k}.ovpn",
                        url,
                        {**data, "location": v},
                    )
                    for k, v in config_locations.items()
                ]

                await asyncio.gather(*tasks)

        if args.c:
            await get_credentials(session)


def main() -> None:
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("user", type=str, help="Windscribe username")
    parser.add_argument("password", type=str, help="Windscribe password")
    parser.add_argument(
        "-z", default=True, action="store_false", help="disable zipfile download"
    )
    parser.add_argument(
        "-c", default=True, action="store_true", help="download credentials"
    )

    args = parser.parse_args()
    logger.debug(args)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(download(args))


if __name__ == "__main__":
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "filename": "app.log",
                "maxBytes": 20971520 * 5,
                "backupCount": 10,
                "encoding": "utf8",
            },
        },
        "root": {"level": "DEBUG", "handlers": ["console"]},
    }

    logging.config.dictConfig(logging_config)
    main()
