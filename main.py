import uuid
from cassandra.cluster import Cluster
import random
import time
import docker
from db import *
from cluster import *
import argparse

def main(container_names, compaction_settings, insert_keys_count, total_ops):
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

    create_table_query += f" WITH compaction = {compaction_settings}"

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
        help="Compaction strategy to use (SizeTieredCompactionStrategy, LeveledCompactionStrategy, TimeWindowCompactionStrategy)",
    )

    parser.add_argument("--insert_keys_count", type=int, default=50000, help="Number of keys to insert")
    parser.add_argument("--total_ops", type=int, default=10000, help="Total number of operations")

    # SizeTiered settings
    parser.add_argument("--bucket_high", type=float, default=1.5)
    parser.add_argument("--bucket_low", type=float, default=0.5)
    parser.add_argument("--min_sstable_size", type=int, default=50)
    parser.add_argument("--num_sstables", type=int, default=4)

    # Leveled settings
    parser.add_argument("--sstable_size_in_mb", type=int, default=160)

    # TimeWindow settings
    parser.add_argument("--compaction_window_unit", type=str, default="DAYS")
    parser.add_argument("--compaction_window_size", type=int, default=1)
    parser.add_argument("--expired_sstable_check_frequency_seconds", type=int, default=60)

    args = parser.parse_args()

    # Construct compaction settings
    compaction_settings = None
    if args.compaction == "SizeTieredCompactionStrategy":
        compaction_settings = {
            "class": args.compaction,
            "bucket_high": args.bucket_high,
            "bucket_low": args.bucket_low,
            "min_sstable_size": args.min_sstable_size,
            "min_threshold": args.num_sstables,
            "max_threshold": args.num_sstables,
        }
    elif args.compaction == "LeveledCompactionStrategy":
        compaction_settings = {
            "class": args.compaction,
            "sstable_size_in_mb": args.sstable_size_in_mb,
        }
    elif args.compaction == "TimeWindowCompactionStrategy":
        compaction_settings = {
            "class": args.compaction,
            "compaction_window_unit": args.compaction_window_unit,
            "compaction_window_size": args.compaction_window_size,
            "expired_sstable_check_frequency_seconds": args.expired_sstable_check_frequency_seconds,
            "min_threshold": args.num_sstables,
            "max_threshold": args.num_sstables,
        }

    main(
        container_names=args.containers,
        compaction_settings=compaction_settings,
        insert_keys_count=args.insert_keys_count,
        total_ops=args.total_ops,
    )
