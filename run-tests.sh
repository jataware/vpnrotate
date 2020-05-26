
#!/bin/sh

curl --silent --fail localhost:8080/healthcheck || exit 1

