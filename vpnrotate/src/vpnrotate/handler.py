import logging
from logging import Logger
from pathlib import Path
from time import perf_counter

from aiohttp import web

from . import __version__, svchandler, utils, vpnconfigs

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
            description: Return connection information
    """
    try:
        provider = request.app["PROVIDER"]
        local_connect = request.app["LOCAL_CONNECT"]
        current_connect = await utils.get_ip_info(extended=False)
        secure = current_connect.get("ip", "") != local_connect.get("ip", "")

        return web.json_response(
            {
                **provider,
                "local": local_connect,
                "current": current_connect,
                "secure": secure,
            }
        )

    except Exception as e:
        logger.exception("vpn info failed")
        raise web.HTTPInternalServerError(text=str(e))


async def vpnsecure(request):
    """
    ---
    summary: Compares container IP with current IP to test if container is "secure"
    tags:
    - VPN Information
    responses:
        "200":
            description: Return yes / no
    """
    try:
        local_connect = request.app["LOCAL_CONNECT"]
        current_connect = await utils.get_ip_info()
        secure = current_connect.get("ip", "") != local_connect.get("ip", "")
        return web.json_response(secure)

    except Exception as e:
        logger.exception("vpn secure failed")
        raise web.HTTPInternalServerError(text=str(e))


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
        request.app["PROVIDER"] = await svchandler.change_vpn_config(
            vpn_env["vpnconfigs"], vpn_env["vpnconfig"], body.get("server")
        )
        await svchandler.restart_vpn()
        return web.Response(text="ok")

    except Exception as e:
        logger.exception("restart failed")
        raise web.HTTPInternalServerError(text=str(e))


async def start_vpn(request):
    """
    ---
    summary: Start vpn with current vpn settings
    tags:
    - VPN
    responses:
        "200":
            description: ok
    """
    try:
        await svchandler.start_vpn()
        return web.Response(text="ok")

    except Exception as e:
        logger.exception("start failed")
        raise web.HTTPInternalServerError(text=str(e))


async def status_vpn(request):
    """
    ---
    summary: returns raw vpn svc status
    tags:
    - VPN
    responses:
        "200":
            description: status string
    """
    try:
        success, rc, stdout = await svchandler.status_vpn()
        if success:
            return web.Response(text=stdout)

        raise Exception(f"Error checking status: {rc}")

    except Exception as e:
        logger.exception("status check failed")
        raise web.HTTPInternalServerError(text=str(e))


async def stop_vpn(request):
    """
    ---
    summary: Stop vpn
    tags:
    - VPN
    responses:
        "200":
            description: ok
    """
    try:
        await svchandler.stop_vpn()
        return web.Response(text="ok")

    except Exception as e:
        logger.exception("stop failed")
        raise web.HTTPInternalServerError(text=str(e))


async def refresh_vpn_configs(request):
    """
    ---
    summary: Refresh vpn configs
    tags:
    - VPN
    responses:
        "200":
            description: ok
    """
    try:
        config = request.app["CONFIG"]
        await vpnconfigs.run_ovpn_setup(config, clean=False)
        return web.Response(text="ok")

    except Exception as e:
        logger.exception("stop failed")
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
            vpn_config_dir = Path(f"{vpn_env['vpnconfigs']}/{vpn}/ovpn_tcp/")
            if not vpn_config_dir.exists():
                continue

            for f in vpn_config_dir.iterdir():
                try:
                    # Filter out crt/key/pem
                    if f.suffix in [".tcp", ".ovpn"]:
                        if vpn == "nordvpn":
                            s = f.with_suffix("").stem
                        else:
                            s = f.stem

                        vpns[vpn].append(s)
                except Exception:
                    logger.exeception("error parsing filename")

        return web.json_response(vpns)

    except Exception as e:
        logger.exception("vpn error")
        raise web.HTTPInternalServerError(text=str(e))


def routing_table(app):
    return [
        web.get("/", index, allow_head=False),
        web.get("/healthcheck", healthcheck, allow_head=False),
        web.get("/metrics", metrics, allow_head=False),
        web.get("/vpns", vpns, allow_head=False),
        web.get("/vpn/status", status_vpn, allow_head=False),
        web.put("/vpn/restart", restart_vpn),
        web.delete("/vpn/stop", stop_vpn),
        web.post("/vpn/start", start_vpn),
        web.get("/vpninfo", vpninfo, allow_head=False),
        web.get("/vpnsecure", vpnsecure, allow_head=False),
        web.post("/vpn/configs", refresh_vpn_configs),
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
