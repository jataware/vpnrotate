
#!/bin/sh

curl --silent --fail localhost:8080/healthcheck || exit 1
curl --silent --fail localhost:8080/redis/ping || exit 1
