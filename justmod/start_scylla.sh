#!/bin/bash

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <number_of_nodes>"
  exit 1
fi

NUM_NODES=$1

# Start the first node
echo "Starting node 1: some-scylla"
docker run --name some-scylla -d scylladb/scylla

# Wait a few seconds for IP to get assigned
sleep 5

SEED_IP=$(docker inspect --format='{{ .NetworkSettings.IPAddress }}' some-scylla)
echo "Seed node IP: $SEED_IP"

# Start the remaining nodes
for i in $(seq 2 $NUM_NODES); do
  NAME="some-scylla${i}"
  echo "Starting node $i: $NAME"
  docker run --name "$NAME" -d scylladb/scylla --seeds="$SEED_IP"
  sleep 2
done
