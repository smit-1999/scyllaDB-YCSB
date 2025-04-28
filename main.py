import uuid
from cassandra.cluster import Cluster
import random
import time
import docker
from cassandra.cluster import Cluster

def get_container_ips(container_names):
    client = docker.from_env()
    ips = []
    for name in container_names:
        try:
            container = client.containers.get(name)
            ip_address = container.attrs['NetworkSettings']['IPAddress']
            ips.append(ip_address)
        except docker.errors.NotFound:
            print(f"❌ Container {name} not found.")
    return ips

# Get IPs of running containers
container_names = ['some-scylla', 'some-scylla2']
node_ips = get_container_ips(container_names)

# Connect to the cluster
cluster = Cluster(node_ips)
session = cluster.connect()


session.execute("""
    CREATE KEYSPACE IF NOT EXISTS ycsb
    WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'}
""")

session.set_keyspace('ycsb')

session.execute("""
    CREATE TABLE IF NOT EXISTS usertable (
        y_id text PRIMARY KEY,
        field0 text
    )
""")

def insert_record(session, id):
    value = "value_" + str(id)
    session.execute(
        "INSERT INTO usertable (y_id, field0) VALUES (%s, %s)",
        (id, value)
    )

# Insert 1000 keys as the load phase
inserted_ids = []
for i in range(1000):
    ycsb_id = str(uuid.uuid4())
    insert_record(session, ycsb_id)
    inserted_ids.append(ycsb_id)


def read_record(session, id):
    session.execute("SELECT * FROM usertable WHERE y_id = %s", (id,))

def update_record(session, id):
    new_value = "value_" + str(random.randint(1, 10000))
    session.execute("UPDATE usertable SET field0 = %s WHERE y_id = %s", (new_value, id))

# Run 1000 operations: 50% reads, 50% updates
total_ops = 1000
start = time.time()

for i in range(total_ops):
    target_id = random.choice(inserted_ids)
    if i % 2 == 0:
        read_record(session, target_id)
    else:
        update_record(session, target_id)

end = time.time()
print(f"Executed {total_ops} ops in {end - start:.2f} seconds")


print("\nVerifying stored records...")

for _ in range(5):
    sample_id = random.choice(inserted_ids)
    row = session.execute("SELECT * FROM usertable WHERE y_id = %s", (sample_id,)).one()

    if row:
        print(f"✅ Found entry: y_id = {row.y_id}, field0 = {row.field0}")
    else:
        print(f"❌ No data found for ID: {sample_id}")