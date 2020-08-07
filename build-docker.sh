#!/usr/bin/env sh


if [ ! -d "nordvpn" ]; then
  mkdir nordvpn
  wget -q -O nordvpn/ovpn_tmp.zip https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip
  unzip -q nordvpn/ovpn_tmp.zip -d nordvpn
  rm nordvpn/ovpn_tmp.zip

  mkdir pia
  wget -q -O pia/pia_tmp.zip https://www.privateinternetaccess.com/openvpn/openvpn-tcp.zip
  unzip -q pia/pia_tmp.zip -d pia
  cp pia/*.ovpn nordvpn/ovpn_tcp/
fi

DT=$(date +"%Y%m%d")
GIT=${DT}.git.$(git rev-parse --short HEAD)
VERSION="0.1.1"
GROUP=jataware
NAME=vpnproxy
IMAGE="${GROUP}/${NAME}"

docker build \
       -t "${IMAGE}:dev" \
       -t "${IMAGE}:${VERSION}" \
       -t "${IMAGE}:${GIT}" \
       -t "${NAME}:${VERSION}" \
       -t "registry.gitlab.com/${IMAGE}:${VERSION}" \
       .
