import logging
import os
import pathlib
from logging import Logger
from time import perf_counter

from aiohttp import web

from . import __version__, svchandler

logger: Logger = logging.getLogger(__name__)

logger: Logger = logging.getLogger(__name__)

"""
Swagger Help: https://swagger.io/docs/specification/describing-parameters/
"""


# Routes
async def index(request):
    return web.Response(text=__version__)


async def restart_vpn(request):
    """
    ---
    summary: Update VPN and restart
    tags:
    - VPN
    requestBody:
      description: Post body
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              vpn:
                type: string
              server:
                type: string
            required:
              - vpn
              - server
          examples:
            example:
              summary: Sample post
              value:
                vpn: nordvpn
                server: us8273.nordvpn.com
    responses:
        "200":
            description: ok
    """
    try:
        body = await request.json()
        vpn_env = request.app["CONFIG"]["vpn_env"]
        await svchandler.changeVPNConfig(
            vpn_env["vpnconfigs"], vpn_env["vpnconfig"], body.get("server")
        )
        await svchandler.restartVPN()
        return web.Response(text="ok")

    except Exception as e:
        logger.exception("restart failed")
        raise web.HTTPInternalServerError(text=str(e))


async def metrics(request):
    """
    ---
    summary: Metrics
    tags:
    - Health Check
    responses:
      "200":
        description: Returns metrics information
        content:
          application/json: {}
    """
    metrics = request.app["METRICS"]
    content = {
        "uptime": perf_counter() - metrics.START_TIME,
        "total_requsts": metrics.TOTAL_REQUESTS.value,
    }
    return web.json_response(content)


async def vpns(request):
    """
    ---
    summary: This end-point returns available vpn servers.
    tags:
    - VPN
    responses:
        "200":
            description: Return "ok" text
        "500":
            description: return error
    """
    try:
        vpns = {"nordvpn": [], "pia": [], "wind": []}

        vpn_env = request.app["CONFIG"]["vpn_env"]

        for vpn in vpns.keys():
            DIR = f"{vpn_env['vpnconfigs']}/{vpn}/ovpn_tcp/"
            temp_vpns = []
            for f in os.listdir(DIR):
                try:
                    # Filter out crt/key/pem
                    if "ovpn" in f:
                        if vpn == "nordvpn":
                            s = f.split(".tcp")
                            temp_vpns.append(s[0])
                        else:
                            s = f.split(".ovpn")
                            temp_vpns.append(s[0])
                        vpns[vpn] = temp_vpns

                except Exception:
                    logger.exeception("error parsing filename")

        return web.json_response(vpns)

    except Exception as e:
        return web.Response(text=e)


async def vpns(request):
    """
    ---
    summary: This end-point returns available vpn servers.
    tags:
    - VPN
    responses:
        "200":
            description: Return "ok" text
        "500":
            description: return error
    """
    try:
        vpn_env = request.app["CONFIG"]["vpn_env"]
        DIR = f"{vpn_env['vpnconfigs']}/ovpn_tcp/"
        all_tcp_vpns = []
        for f in os.listdir(DIR):
            try:
                s = f.split(".tcp")
                if "nord" in s[0]:
                    all_tcp_vpns.append(s[0])
                else:
                    all_tcp_vpns.append(pathlib.Path(s[0]).stem)
            except Exception:

                logger.exeception("error parsing filename")
        return web.json_response({"vpns": all_tcp_vpns})
    except Exception as e:
        return web.Response(text=e)


def routing_table(app):
    return [
        web.get("/", index, allow_head=False),
        web.get("/metrics", metrics, allow_head=False),
        web.get("/vpns", vpns, allow_head=False),
        web.put("/vpn/restart", restart_vpn),
    ]


@web.middleware
async def request_counter(request, handler):
    request.app["METRICS"].TOTAL_REQUESTS.increment()
    response = await handler(request)
    return response


@web.middleware
async def response_time(request, handler):
    start_request = perf_counter()
    response = await handler(request)
    response_time = perf_counter() - start_request
    response.headers["x-app-response-time"] = f"{response_time:.8f}"
    return response
