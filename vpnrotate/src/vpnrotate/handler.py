from time import perf_counter

from aiohttp import web

from . import __version__, nordvpnapi, svchandler

import os
"""
Swagger Help: https://swagger.io/docs/specification/describing-parameters/
"""


# Routes
async def index(request):
    return web.Response(text=__version__)


async def secure(request):
    """
    ---
    summary: This end-point allow to test if the vpn is up
    tags:
    - VPN
    responses:
        "200":
            description: Return true|false
    """
    resp = await nordvpnapi.getSecure()
    headers = {f"x-nordvpn-{k}": v for k, v in resp.items()}
    return web.Response(
        text=str(resp.get("status", "") == "Protected").lower(), headers=headers
    )


async def countries(request):
    """
    ---
    summary: Get recommendations
    tags:
    - VPN
    responses:
        "200":
            description: country list
    """
    country_code = request.app["COUNTRY_CODES"]
    return web.json_response(list(country_code.keys()))


async def recommend(request):
    """
    ---
    summary: Get recommendations
    tags:
    - VPN
    parameters:
      - in: query
        name: country
        schema:
          type: string
        description: country code for filter
    responses:
        "200":
            description: recommendation list
    """
    params = request.rel_url.query
    country = params.get("country", "").lower()
    country_code = request.app["COUNTRY_CODES"].get(country)
    resp = await nordvpnapi.getRecommendations(country_code=country_code)
    return web.json_response(resp)


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
              server:
                type: string
            required:
              - server
          examples:
            example:
              summary: Sample post
              value:
                server: us5567.nordvpn.com
    responses:
        "200":
            description: ok
    """
    body = await request.json()
    vpn_env = request.app["CONFIG"]["vpn_env"]
    await svchandler.changeVPNConfig(
        vpn_env["vpnconfigs"], vpn_env["vpnconfig"], body.get("server")
    )
    await svchandler.restartVPN()
    return web.Response(text="ok")


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
        DIR = '/etc/ovpn/configs/ovpn_tcp/'
        all_tcp_vpns=[]
        for f in os.listdir(DIR):
            print(f)
            try:
                s = f.split('.tcp')
                if 'nord' in s[0]:
                    all_tcp_vpns.append(s[0])
                else:
                    all_tcp_vpns.append(s[0][:-5])
            except Exception as e:
                print("error: " , e)
        return web.json_response({"vpns":all_tcp_vpns})
    except Exception as e:
        return web.Response(text=e)

def routing_table(app):
    return [
        web.get("/", index, allow_head=False),
        web.get("/healthcheck", healthcheck, allow_head=False),
        web.get("/metrics", metrics, allow_head=False),
        web.get("/secure", secure, allow_head=False),
        web.get("/countries", countries, allow_head=False),
        web.get("/recommend", recommend, allow_head=False),
        web.get('/vpns', vpns, allow_head=False),
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
