import logging
from logging import Logger

from aiohttp import web
from aiohttp_swagger3 import SwaggerDocs, SwaggerUiSettings  # noqa: I201

from . import __version__, config, handler, metrics, utils, vpnconfigs

logger: Logger = logging.getLogger(__name__)


async def startup_handler(app: web.Application) -> None:
    logger.info("starting up")
    config = app["CONFIG"]
    if config["vpn_env"]["reload_configs_on_startup"]:
        await vpnconfigs.run_ovpn_setup(config, clean=True)

    app["METRICS"] = metrics.Metrics
    app["LOCAL_CONNECT"] = await utils.get_ip_info(
        config["vpn_env"]["ip"], extended=True
    )
    app["PROVIDER"] = {}


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
