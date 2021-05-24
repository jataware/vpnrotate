


# Quick Start

```
export NORDUSER="<user>"
export NORDPASS="<pass>"
export PIAUSER="<user>"
export PIAPASS="<user>"
export WINDUSER="<user"
export WINDPASS="<pass>"

# to check environment variables are correct
env

# To download VPN files
./ovpn-download-aws.sh

# Build and spin up the container
./build-docker.sh

docker-compose up -d
```
Swagger docs http://localhost:8080/api/docs/


# Getting Started

Setup a python 3.8+ virtual env

- https://github.com/pyenv/pyenv <br>
- https://github.com/pyenv/pyenv-virtualenv <br>


Install Dev Requirements

```
python -m pip install -r requirements-dev.txt
```



## Tox

Reformat Code (runs isort, black)

```
tox -e format
```


Test + Lint

```
tox
```


Package
```
tox -e package
```


## Docker

```
./build-docker.sh
```


## Docker Compose

```
docker-compose up -d --build



docker-compose stop
```



## Dev

```
python -m pip install -e .

vpnrotate --config=app.dev.yaml --logging=logging.yaml
```


## Bump Version


See [bump2version](https://github.com/c4urself/bump2version)

Bump version, verify changes and commit to branch.

Example:

```
bump2version --current-version 0.1.6 --new-version 0.1.7 minor --allow-dirty
```
