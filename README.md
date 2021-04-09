


# Quick Start

```
export NORDUSER="<user>"
export NORDPASS="<pass>"
export PIAUSER="<user>"
export PIAPASS="<user>"
export WINDUSER="<user"
export WINDPASS="<pass>"

export SERVER=us6053.nordvpn.com

# to check environment variables are correct
env

# To download VPN files
./ovpn-download.sh

# Build and spin up the container
./build-docker.sh

docker-compose up -d

# check if
curl -vv -Lx localhost:8118 localhost:8080/secure

# change vpn and restart vpn service
curl -X PUT "http://localhost:8080/vpn/restart" \
     -H "Content-Type: application/json" \
     -d "{\"server\":\"us5426.nordvpn.com\"}"
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
