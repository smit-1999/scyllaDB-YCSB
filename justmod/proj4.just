set working-directory := '..'
set shell := ["bash","-cu"]

# install extra dependencies
deps:
    pwd
    # Fill here.

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


start-client compaction_strategy="SizeTieredCompactionStrategy" compaction_log_dir="./CompactionLogs/" insert_keys_count="100" total_ops="10" containers="some-scylla":
    @echo "Client started."
    mkdir -p {{compaction_log_dir}}

    # Run the client with dynamically generated containers
    sudo python3 main.py --containers {{containers}} --compaction {{compaction_strategy}} --insert_keys_count {{insert_keys_count}} --total_ops {{total_ops}} &> {{compaction_log_dir}}{{compaction_strategy}}_{{insert_keys_count}}_{{total_ops}}.log

    @echo "Client finished."
# NOTE: feel free to add more recipes as you see fit...
#       also feel free to add extra parameters to the recipes as you see fit,
#       but don't change the existing parameters

python_run := if `which uv || true` != "" { "uv run" } else { "python3" }
