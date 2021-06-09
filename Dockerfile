
FROM python:3.9-slim-buster
# See https://nordvpn.com/servers/tools for recommendations

ENV PROTOCOL="tcp" \
    LOCAL_NETWORK=192.168.1.0/24

RUN apt-get update && apt-get clean && apt-get install -y \
      privoxy \
      openvpn \
      runit \
      gcc \
      musl-dev \
      curl \
      dnsutils \
      mg \
      vim

RUN rm -rf /var/lib/apt/lists/* \
    && mkdir -p /etc/runonce/ \
    && mkdir -p /var/log/ovpn /var/log/privoxy /var/log/vpnrotate /etc/ovpn/configs

COPY vpnrotate/ /etc/vpnrotate
RUN pip3 install --upgrade pip && \
    pip3 install /etc/vpnrotate

COPY service /etc/service/
CMD ["runsvdir", "/etc/service"]
