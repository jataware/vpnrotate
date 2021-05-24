#!/usr/bin/env sh

set -e

VERSION="0.1.7"

printf "${GITLAB_PASS}\n" | docker login registry.gitlab.com/jataware -u "${GITLAB_USER}" --password-stdin

echo "push vpnrotate ${VERSION}"
docker push "registry.gitlab.com/jataware/vpnproxy:${VERSION}"

