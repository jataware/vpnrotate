#!/usr/bin/env sh

DT=$(date +"%Y%m%d")
GIT=${DT}.git.$(git rev-parse --short HEAD)

VERSION="0.2.4"

GROUP=jataware
NAME=vpnproxy
IMAGE="${GROUP}/${NAME}"

docker build \
       -t "${IMAGE}:dev" \
       -t "${IMAGE}:${VERSION}" \
       -t "${IMAGE}:${GIT}" \
       -t "${NAME}:${VERSION}" \
       -t "registry.gitlab.com/${IMAGE}:${VERSION}" \
       -t "registry.gitlab.com/${IMAGE}:${VERSION}-dev" \
       -t "jataware/vpnrotate:${VERSION}-dev" \
       -t "jataware/vpnrotate:${VERSION}" \
       -t "jataware/vpnrotate:latest" \
       .
