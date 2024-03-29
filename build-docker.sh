#!/usr/bin/env sh

DT=$(date +"%Y%m%d")
GIT=${DT}.git.$(git rev-parse --short HEAD 2>/dev/null || echo "norev")

VERSION="0.3.1"

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
