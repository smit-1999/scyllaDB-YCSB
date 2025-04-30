#!/bin/bash

docker run --name some-scylla -d scylladb/scylla

# Wait a few seconds for IP to get assigned
sleep 5

SEED_IP=$(docker inspect --format='{{ .NetworkSettings.IPAddress }}' some-scylla)
docker run --name some-scylla2 -d scylladb/scylla --seeds="$SEED_IP"
