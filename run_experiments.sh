#!/bin/bash
set -e

# Define experiment parameters
OPS_LIST=("1000" "10000" "100000")
KEYS_LIST=("10000" "100000")
NODE_COUNTS=("1" "2")
COMPACTIONS=("SizeTieredCompactionStrategy" "LeveledCompactionStrategy" "TimeWindowCompactionStragety")
LOG_DIR="./CompactionLogs"

mkdir -p "$LOG_DIR"

wait_for_cluster_up() {
  local expected_nodes=$1
  echo "⏳ Waiting for $expected_nodes Scylla nodes to be UP..."

  for i in {1..30}; do  # Retry up to 30 times (~60 seconds)
    # Try fetching nodetool status, capture output and ignore failure
    output=$(sudo docker exec -i some-scylla nodetool status 2>/dev/null || true)

    # Count lines that begin with "UN"
    up_count=$(echo "$output" | grep -c "^UN")

    echo "▶️  Detected $up_count/$expected_nodes nodes UP..."

    if [ "$up_count" -eq "$expected_nodes" ]; then
      echo "✅ All $expected_nodes nodes are UP."
      return 0
    fi

    sleep 2
  done

  echo "⚠️ Timed out waiting for $expected_nodes nodes to become UP. Proceeding anyway..."
  return 0  # Do not exit with error
}

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
          "$CONTAINERS"

        # Stop cluster
        just p4::stop-cluster "$nodes"

        echo "✅ Completed: Nodes=$nodes, Ops=$ops, Keys=$keys, Compaction=$strategy"
        echo ""

      done
    done
  done
done
echo "All experiments completed."