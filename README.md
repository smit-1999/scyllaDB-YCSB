# scyllaDB-YCSB
Test repository for scyllaDB on YCSB workloads
Repo install: curl -sSf get.scylladb.com/server | sudo bash

Docker Setup as docker needed for running ScyllaDB instance:
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo docker run hello-world

Download image of ScyllaDB
sudo docker pull scylladb/scylla

To start a one-node ScyllaDB instance:
sudo docker run --name scylla -d scylladb/scylla

To list all Docker containers running:
sudo docker ps

To close a docker container 
sudo docker stop scylla

ScyllaDB installation command:
sudo curl -sSf get.scylladb.com/server | sudo bash

ScyllaDb status: To verify that the cluster is up and running:
sudo docker exec -it scylla nodetool status
