import uuid
from cassandra.cluster import Cluster
import random
import time
import docker
from db import *
from cluster import *
import argparse

insert_keys_count = 50000
total_ops = 10000


def main(container_names, compaction):
    # Get IPs of running containers
    # container_names = ['some-scylla-with-compaction', 'some-scylla2-with-compaction']
    node_ips = get_container_ips(container_names)

    # Connect to the cluster
    cluster = Cluster(node_ips)
    session = cluster.connect()

    session.execute(
        """
        CREATE KEYSPACE IF NOT EXISTS ycsb
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
    """
    )
    session.set_keyspace("ycsb")
    create_table_query = """
        CREATE TABLE IF NOT EXISTS usertable (
            y_id text PRIMARY KEY,
            field0 text
        )
    """

    if compaction:
        compaction_json = f"{{'class': '{compaction}'}}"
        create_table_query += f" WITH compaction = {compaction_json}"

    print(f"Executing:\n{create_table_query}\n")
    session.execute(create_table_query)

    # Insert keys as the load phase
    inserted_ids = []
    insert_start_time = time.time()

    for i in range(insert_keys_count):
        ycsb_id = str(uuid.uuid4())
        insert_record(session, ycsb_id)
        inserted_ids.append(ycsb_id)
        if i % 1000 == 0:
            print(f"Inserted {i} ops in {time.time() - insert_start_time:.2f} seconds")
    insert_end_time = time.time()
    print(
        f"Executed {insert_keys_count} ops in {insert_end_time - insert_start_time:.2f} seconds"
    )

    # Run total_ops operations: 50% reads, 50% updates

    start = time.time()

    for i in range(total_ops):
        target_id = random.choice(inserted_ids)
        if i % 1000 == 0:
            print(f"Executed {i} ops in {time.time() - start:.2f} seconds")
        if i % 2 == 0:
            read_record(session, target_id)
        else:
            update_record(session, target_id)

    end = time.time()
    print(f"Executed {total_ops} ops in {end - start:.2f} seconds")

    print("\nVerifying stored records...")

    for _ in range(5):
        sample_id = random.choice(inserted_ids)
        row = session.execute(
            "SELECT * FROM usertable WHERE y_id = %s", (sample_id,)
        ).one()

        if row:
            print(f"✅ Found entry: y_id = {row.y_id}, field0 = {row.field0}")
        else:
            print(f"❌ No data found for ID: {sample_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ScyllaDB YCSB Workload Runner")

    parser.add_argument(
        "--containers",
        nargs="+",
        default=["some-scylla-with-compaction", "some-scylla2-with-compaction"],
        help="List of Scylla container names (space separated)",
    )

    parser.add_argument(
        "--compaction",
        type=str,
        default=None,
        help="Compaction strategy to use, e.g., \"{'class': 'LeveledCompactionStrategy'}\" (default: no compaction)",
    )

    args = parser.parse_args()

    main(args.containers, args.compaction)
