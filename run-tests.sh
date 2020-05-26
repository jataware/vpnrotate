
#!/bin/sh

sleep 2

curl --silent --fail localhost:8080/healthcheck || exit 1

