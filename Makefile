
# Dependencies

# gnumake curl git
# pyenv pyenv-virtualenv

# https://github.com/pyenv/pyenv-installer
# https://github.com/pyenv/pyenv
# https://github.com/pyenv/pyenv-virtualenv
# osx: brew install pyenv pyenv-virtualenv


VERSION := 0.2.4

DEV ?= $(strip $(if $(findstring y,$(prod)),,dev))

VERSION := ${VERSION}$(DEV:dev=-dev)

DETECTED_OS := $(shell uname)

CMD_ARGUMENTS ?= $(cmd)

.DEFAULT_GOAL := help

check-%:
	@: $(if $(value $*),,$(error $* is undefined))

help:
	@echo ""
	@echo "By default make targets assume DEV to run production pass in prod=y as a command line argument"
	@echo ""
	@echo "Targets:"
	@echo ""
	@grep -E '^([a-zA-Z_-])+%*:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}'


## Helpers

.PHONY: yN
yN:
		@echo "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ] || (echo "aborted."; exit 1;)

ip-addr:
ifeq ($(DETECTED_OS),Darwin)        # Mac OS X
	$(eval IP_ADDRESS=$(shell ipconfig getifaddr en0))
else
	$(eval IP_ADDRESS=$(shell hostname -i))
endif

.PHONY: print-version
print-version:
	@echo "Version: ${VERSION}"


.PHONY: docker_build
docker_build: docker_build_vpnproxy ## Build all docker containers

.PHONY: docker_build_vpnproxy
docker_build_vpnproxy: ## build vpnproxy container
	./build-docker.sh


tox-%: ## Run tox on
	@echo "tox $*"
	(cd $* && tox -e format && tox)

.PHONY: tox
tox: tox-vpnrotate ## Run tox on vpnrotate

.PHONY: fmt
fmt: ## Run python formatter
	(cd vpnrotate && tox -e format)

docker_login:| check-GITLAB_USER check-GITLAB_PASS  ## Login to docker registery. Requires GITLAB_USER and GITLAB_PASS to be set in the environment
	@printf "${GITLAB_PASS}\n" | docker login registry.gitlab.com/jataware -u "${GITLAB_USER}" --password-stdin

.PHONY: docker_push
docker_push: docker_push_vpnproxy  docker_login  ## push all containers to docker registry

.PHONY: docker_push_vpnproxy
docker_push_vpnproxy:| docker_login ## push proxy container to docker registry
	@echo "push vpnproxy ${VERSION}"
	docker push "registry.gitlab.com/jataware/vpnproxy:${VERSION}"

.PHONY: docker-compose_up
docker-compose_up:| ip-addr ## Start docker-compose instance local
	docker-compose up -d


.PHONY: docker_login-dockerhub
docker_login-dockerhub:| check-DOCKERHUB_USER check-DOCKERHUB_TOKEN  ## Login to docker registery. Requires DOCKERHUB_USER and DOCKERHUB_TOKEN to be set in the environment
	@printf "${DOCKERHUB_TOKEN}\n" | docker login -u "${DOCKERHUB_USER}" --password-stdin


.PHONY: docker_push-dockerhub
docker_push-dockerhub:| docker_login-dockerhub  ## Pushes docker image to docker hub
	@echo "push ${VERSION} "
	docker push "jataware/vpnrotate:${VERSION}"
	docker push "jataware/vpnrotate:latest"

.PHONY: draft-release
draft-release:
	gh release create "v${VERSION}" --generate-notes -d
