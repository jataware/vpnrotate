import json
import logging
import os
from logging import Logger
from time import perf_counter

from aiohttp import web

from . import __version__, svchandler

logger: Logger = logging.getLogger(__name__)


"""
Swagger Help: https://swagger.io/docs/specification/describing-parameters/
"""


# Routes
async def index(request):
    return web.Response(text=__version__)


async def vpninfo(request):
    """
    ---
    summary: Returns current VPN information
    tags:
    - VPN Information
    responses:
        "200":
            description: Return "ok" text
    """
    try:
        # Get vpn provider/server info
        try:
            vpn_env = request.app["CONFIG"]["vpn_env"]
            fdir = f"{vpn_env['vpnconfigs']}/local_connect/provider.txt"
            with open(fdir) as json_file:
                provider = json.load(json_file)

        except FileNotFoundError:
            provider = {"provider": "none", "server": "none"}

        # get if secure connection
        try:
            vpn_env = request.app["CONFIG"]["vpn_env"]
            fdir = f"{vpn_env['vpnconfigs']}/local_connect/local_connect.json"
            content = svchandler.is_secure(fdir)
            secure = {"connected": content["secure"]}

        except Exception:
            secure = {"connected": False}
            return secure

        # Get VPN info
        cmd = "curl -s ipinfo.io/$(curl -s ifconfig.me)"
        vpn_info = svchandler.curlit(cmd)

        all_info = {**provider, **secure, **vpn_info}

        return web.json_response(all_info)

    except Exception as e:
        return web.Response(text=str(e))


async def vpnsecure(request):
    """
    ---
    summary: Compares container IP with current IP to test if container is "secure"
    tags:
    - VPN Information
    responses:
        "200":
            description: Return "ok" text
    """
    try:
        # Read in local machine IP information
        vpn_env = request.app["CONFIG"]["vpn_env"]
        fdir = f"{vpn_env['vpnconfigs']}/local_connect/local_connect.json"

        content = svchandler.is_secure(fdir)

        return web.json_response(content)

    except Exception as e:
        return web.Response(text=str(e))


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
                server: us6782.nordvpn.com
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


async def healthcheck(request):
    """
    ---
    summary: This end-point allow to test that service is up.
    tags:
    - Health Check
    responses:
        "200":
            description: Return "ok" text
    """
    return web.Response(text="ok")


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


def routing_table(app):
    return [
        web.get("/", index, allow_head=False),
        web.get("/healthcheck", healthcheck, allow_head=False),
        web.get("/metrics", metrics, allow_head=False),
        web.get("/vpns", vpns, allow_head=False),
        web.put("/vpn/restart", restart_vpn),
        web.get("/vpninfo", vpninfo, allow_head=False),
        web.get("/vpnsecure", vpnsecure, allow_head=False),
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
