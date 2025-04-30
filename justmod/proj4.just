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
start-cluster:
    pwd &&\
    chmod +x ./justmod/start_scylla.sh &&\
    ./justmod/start_scylla.sh
    @echo "ScyllaDB 3-node cluster started."

stop-cluster:
    pwd &&\
    chmod +x ./justmod/stop_scylla.sh &&\
    ./justmod/stop_scylla.sh
    @echo "ScyllaDB 3-node cluster stopped."

start-client compaction_strategy="SizeTieredCompactionStrategy" compaction_log_dir="./CompactionLogs/":
    @echo "Client started."
    mkdir -p {{compaction_log_dir}}
    sudo python3 main.py --containers some-scylla some-scylla2 --compaction {{compaction_strategy}} &> {{compaction_log_dir}}{{compaction_strategy}}.log
    @echo "Client finished."
    

# NOTE: feel free to add more recipes as you see fit...
#       also feel free to add extra parameters to the recipes as you see fit,
#       but don't change the existing parameters

python_run := if `which uv || true` != "" { "uv run" } else { "python3" }
