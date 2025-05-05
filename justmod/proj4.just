set working-directory := '..'
set shell := ["bash","-cu"]

# install extra dependencies
deps:
    sudo apt update && \
    sudo apt install python3-pip && \
    pip3 install cassandra-driver && \
    sudo apt-get update && \
    sudo apt-get install ca-certificates curl && \
    sudo install -m 0755 -d /etc/apt/keyrings && \
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc && \
    sudo chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" |   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null  && \
    sudo apt-get update && \
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin && \
    sudo docker run hello-world && \
    sudo docker pull scylladb/scylla && \
    sudo curl -sSf get.scylladb.com/server | sudo bash && \
    sudo pip3 install cassandra-driver && \
    sudo pip3 install docker

# build your executables in release mode
check-container-status container_name="some-scylla":
    sudo docker exec -it {{container_name}} nodetool status
    # Fill here.

# run your executables
start-cluster num_nodes="3":
    chmod +x ./justmod/start_scylla.sh &&\
    ./justmod/start_scylla.sh {{num_nodes}}
    @echo "ScyllaDB {{num_nodes}}-node cluster started."
    sleep 10
    # @echo "Checking cluster status..."
    # sudo docker exec -it some-scylla nodetool status
    # @echo "Cluster status checked."

stop-cluster num_nodes="3":
    chmod +x ./justmod/stop_scylla.sh &&\
    ./justmod/stop_scylla.sh {{num_nodes}}
    @echo "ScyllaDB {{num_nodes}}-node cluster stopped."


start-client compaction_strategy="SizeTieredCompactionStrategy" compaction_log_dir="./CompactionLogs/" insert_keys_count="100" total_ops="10" containers="some-scylla" node_count="1" workload="a":
    @echo "Client started."
    mkdir -p {{compaction_log_dir}}

    # Run the client with dynamically generated containers
    sudo python3 main.py --containers {{containers}} --compaction {{compaction_strategy}} --insert_keys_count {{insert_keys_count}} --total_ops {{total_ops}} &> {{compaction_log_dir}}{{compaction_strategy}}_{{insert_keys_count}}keys_{{total_ops}}ops_{{node_count}}nodes_{{workload}}workload.log

    @echo "Client finished."

python_run := if `which uv || true` != "" { "uv run" } else { "python3" }
