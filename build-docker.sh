#!/usr/bin/env sh


if [ ! -d "nordvpn" ]; then
  mkdir nordvpn
  wget -q -O nordvpn/ovpn_tmp.zip https://downloads.nordcdn.com/configs/archives/servers/ovpn.zip
  unzip -q nordvpn/ovpn_tmp.zip -d ovpn
  rm nordvpn/ovpn_tmp.zip
fi

DT=$(date +"%Y%m%d")
GIT=${DT}.git.$(git rev-parse --short HEAD)
VERSION="0.1"
IMAGE=jataware/vpnproxy

docker build -t "${IMAGE}:dev" -t "${IMAGE}:${VERSION}" -t "${IMAGE}:${GIT}" .
