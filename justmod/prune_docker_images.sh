#!/bin/bash

# Stop all running containers
docker stop $(docker ps -q)

# Remove all containers
docker rm $(docker ps -a -q)

# Remove all images
docker rmi -f $(docker images -q)

# Remove all volumes
docker volume rm $(docker volume ls -q)

# Remove all networks (except default ones)
docker network rm $(docker network ls | grep -v "bridge\|host\|none" | awk '{print $1}')

# Prune any remaining stuff (dangling images, build cache, etc.)
docker system prune -af
docker volume prune -f
