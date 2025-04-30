#!/bin/bash

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <number_of_nodes>"
  exit 1
fi

NUM_NODES=$1

for i in $(seq 1 $NUM_NODES); do
  if [ "$i" -eq 1 ]; then
    NAME="some-scylla"
  else
    NAME="some-scylla${i}"
  fi

  echo "Stopping and removing $NAME"
  sudo docker stop "$NAME" || true
  sudo docker rm "$NAME" || true
done
