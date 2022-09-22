import argparse
import logging
import logging.config
import os
import sys
from typing import Any, Final, List, Optional

import trafaret as t

# flake and black fight over this order
import yaml  # noqa: I201, I100
from aiohttp import web  # noqa: I201, I100

ENV_LOG_CONFIG: Final = "LOG_CONFIG"


def setup_logging(
    default_path="logging.yaml", default_level=logging.INFO, env_key=ENV_LOG_CONFIG
):

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "rt") as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def load_settings(path):
    with open(path, "rt") as f:
        return yaml.safe_load(f.read())


app_config = t.Dict(
    {
        t.Key("app"): t.Dict(
            {
                "host": t.String(),
                "port": t.Int(),
            }
        ),
        t.Key("vpn_env"): t.Dict(
            {
                "ip": t.String(),
                "vpnconfigs": t.String(),
                "reload_configs_on_startup": t.Bool(),
                "vpnconfig": t.String(),
            }
        ),
        t.Key("wind"): t.Dict(
            {
                "url": t.String(),
            }
        ),
        t.Key("swagger_base_path"): t.String(),
    }
)


def get_config() -> Any:
    try:
        parser = argparse.ArgumentParser(add_help=False)
        required = parser.add_argument_group("required arguments")  # noqa: F841
        optional = parser.add_argument_group("optional arguments")

        # Add back help
        optional.add_argument(
            "-h",
            "--help",
            action="help",
            default=argparse.SUPPRESS,
            help="show this help message and exit",
        )

        optional.add_argument(
            "--resources",
            type=str,
            default=os.getenv("APP_RESOURCES", f"{os.getcwd()}/resources"),
            help="Directory for application resources to be loaded",
        )

        optional.add_argument(
            "--config",
            type=str,
            default=os.getenv("APP_CONFIG", "app.yaml"),
            help="App config file name in resources directory",
        )

        optional.add_argument(
            "--logging",
            type=str,
            default=os.getenv("APP_LOGGING", "logging.yaml"),
            help="App logging files name in resources directory",
        )

        options = parser.parse_args()
        settings = load_settings(f"{options.resources}/{options.config}")

        if ovpn_download_on_start := os.getenv("OVPN_DOWNLOAD_ON_START"):
            settings["vpn_env"]["reload_configs_on_startup"] = (
                True if yaml.safe_load(ovpn_download_on_start) is True else False
            )

        settings["swagger_base_path"] = os.getenv("SWAGGER_BASE_PATH", "/")

        app_config.check(settings)
        setup_logging(f"{options.resources}/{options.logging}")
        return settings

    except Exception:
        parser.print_help(sys.stderr)
        raise
    return None


def init_config(app: web.Application, config: Optional[List[str]] = None) -> None:
    app["CONFIG"] = config
