import uuid
from cassandra.cluster import Cluster
import random
import time
import docker

def insert_record(session, id):
    value = "value_" + str(id)
    session.execute(
        "INSERT INTO usertable (y_id, field0) VALUES (%s, %s)",
        (id, value)
    )

def read_record(session, id):
    session.execute("SELECT * FROM usertable WHERE y_id = %s", (id,))

def update_record(session, id):
    new_value = "value_" + str(random.randint(1, 10000))
    session.execute("UPDATE usertable SET field0 = %s WHERE y_id = %s", (new_value, id))

def read_modify_write(session, id):
    # Step 1: Read the current value (not strictly needed for write, but included for realism)
    result = session.execute("SELECT field0 FROM usertable WHERE y_id = %s", (id,))
    current_value = None
    for row in result:
        current_value = row.field0  # Assume field0 exists and is being modified

    # Step 2: Modify the value (e.g., append something or generate new one)
    # Here, we simply simulate a new value as in update_record
    new_value = "rmw_" + str(random.randint(1, 10000))

    # Step 3: Write back
    session.execute("UPDATE usertable SET field0 = %s WHERE y_id = %s", (new_value, id))
