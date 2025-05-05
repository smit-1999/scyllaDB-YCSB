#!/bin/bash
set -e

# Define experiment parameters
OPS_LIST=("100")
KEYS_LIST=("100")
NODE_COUNTS=("1")
COMPACTIONS=("SizeTieredCompactionStrategy")
WORKLOADS=("a" "b" "c" "d" "f")
LOG_DIR="./CompactionLogs"

mkdir -p "$LOG_DIR"

for workload in "${WORKLOADS[@]}"; do
  for ops in "${OPS_LIST[@]}"; do
    for keys in "${KEYS_LIST[@]}"; do
      for nodes in "${NODE_COUNTS[@]}"; do
        for strategy in "${COMPACTIONS[@]}"; do

          echo "🟢 Starting experiment: Nodes=$nodes, Ops=$ops, Keys=$keys, Compaction=$strategy"
          
          # Start cluster
          just p4::start-cluster "$nodes"

          sleep_interval=$((nodes * 60))  # 60 seconds per node
          echo "⏳ Waiting for $sleep_interval seconds for nodes to start..."
          sleep $sleep_interval  # Wait for nodes to start

          # Generate a list of container names dynamically
          CONTAINERS="some-scylla"
          for i in $(seq 2 {{num_nodes}}); do
              CONTAINERS="$CONTAINERS some-scylla$i";
          done
          echo "Containers: $CONTAINERS"
          # Run client
          just p4::start-client \
            "$strategy" \
            "$LOG_DIR/" \
            "$keys" \
            "$ops" \
            "$CONTAINERS" \
            "$nodes" \
            "$workload" \

          # Stop cluster
          just p4::stop-cluster "$nodes"

          echo "✅ Completed: Nodes=$nodes, Ops=$ops, Keys=$keys, Compaction=$strategy"
          echo ""

        done
      done
    done
  done
done

echo "All experiments completed."