#!/usr/bin/env sh

DT=$(date +"%Y%m%d")
GIT=${DT}.git.$(git rev-parse --short HEAD)

VERSION="0.1.5"

GROUP=jataware
NAME=vpnproxy
IMAGE="${GROUP}/${NAME}"


# Get local machine IP info
mkdir -p ovpn_configs/local_connect
cp provider.txt ovpn_configs/local_connect/provider.txt
curl -s ipinfo.io/$(curl -s ifconfig.me) > ovpn_configs/local_connect/local_connect.json

docker build \
       -t "${IMAGE}:dev" \
       -t "${IMAGE}:${VERSION}" \
       -t "${IMAGE}:${GIT}" \
       -t "${NAME}:${VERSION}" \
       -t "registry.gitlab.com/${IMAGE}:${VERSION}" \
       -t "registry.gitlab.com/${IMAGE}:${VERSION}-dev" \
       .
