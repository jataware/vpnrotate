import logging
from logging import Logger

from aiohttp import web
from aiohttp_swagger3 import SwaggerDocs, SwaggerUiSettings  # noqa: I201

from . import __version__, config, handler, metrics

logger: Logger = logging.getLogger(__name__)

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
    "connection": "keep-alive",
    "cache-control": "max-age=0",
    "accept": "*/*",
    "accept-language": "en-US;q=1.0,en;q=0.9",
}

async def get_ip_info():
    async with aiohttp.ClientSession(raise_for_status=True, headers=HEADERS) as session:
        async with session.get('http://ifconfig.me/ip') as resp:
            ip = await resp.text()
        async with session.get(
                f"http://ipinfo.io/{ip}",
                headers={**HEADERS, "accept": "application/json"}) as resp:
            return await resp.json()


async def startup_handler(app: web.Application) -> None:
    logger.info("starting up")
    app["METRICS"] = metrics.Metrics
    app["LOCAL_CONNECT"] = await get_ip_info()


async def shutdown_handler(app: web.Application) -> None:
    logger.info("shuting down")
    logger.info("shutdown")


def main() -> None:
    settings = config.get_config()
    app = web.Application(
        client_max_size=5 * 1024 ** 2,
        middlewares=[handler.response_time, handler.request_counter],
    )
    swagger = SwaggerDocs(
        app,
        swagger_ui_settings=SwaggerUiSettings(path="/api/docs/"),
        title="vpnrotate",
        version=__version__,
    )
    config.init_config(app, settings)
    app.on_startup.append(startup_handler)
    app.on_cleanup.append(shutdown_handler)
    swagger.add_routes(handler.routing_table(app))
    web.run_app(
        app,
        host=settings["app"]["host"],
        port=settings["app"]["port"],  # access_log=None,
    )


if __name__ == "__main__":
    main()
