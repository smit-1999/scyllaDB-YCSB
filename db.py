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