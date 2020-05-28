
# FROM alpine:3.11.6
FROM python:3.8.3-alpine3.11
# See https://nordvpn.com/servers/tools for recommendations

ENV LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8 \
    USERNAME="" \
    PASSWORD="" \
    PROTOCOL="tcp" \
    SERVER="" \
    LOCAL_NETWORK=192.168.1.0/24

RUN apk --update --no-cache add \
      privoxy \
      openvpn \
      runit \
      gcc \
      musl-dev

RUN rm -rf /var/cache/apk/* \
    && mkdir -p /etc/runonce/ \
    && mkdir -p /var/log/ovpn /var/log/privoxy /var/log/vpnrotate

COPY vpnrotate/ /etc/vpnrotate
RUN pip3 install /etc/vpnrotate

EXPOSE 8118 8080

COPY service /etc/service/
VOLUME [ "/app/ovpn/config" ]

CMD ["runsvdir", "/etc/service"]
