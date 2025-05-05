import random
import time
from db import *
from cluster import *

def print_progress(i, start):
    print(f"Executed {i} ops in {time.time() - start:.2f} seconds")
        
def workload_a(session, inserted_ids, total_ops, start):
    for i in range(total_ops):
        target_id = random.choice(inserted_ids)
        if i % 1000 == 0:
            print(f"Executed {i} ops in {time.time() - start:.2f} seconds")
        if random.random() < 0.5:
            read_record(session, target_id)
        else:
            update_record(session, target_id)

def workload_b(session, inserted_ids, total_ops, start):
    
    for i in range(total_ops):
        target_id = random.choice(inserted_ids)
        if i % 1000 == 0:
            print(f"Executed {i} ops in {time.time() - start:.2f} seconds")
        if random.random() < 0.95:
            read_record(session, target_id)
        else:
            update_record(session, target_id)

def workload_c(session, inserted_ids, total_ops, start):
    
    for i in range(total_ops):
        target_id = random.choice(inserted_ids)
        if i % 1000 == 0:
            print(f"Executed {i} ops in {time.time() - start:.2f} seconds")
        read_record(session, target_id)

def workload_d(session, inserted_ids, total_ops, start):
    
    for i in range(total_ops):
        if i % 1000 == 0:
            print(f"Executed {i} ops in {time.time() - start:.2f} seconds")
        if random.random() < 0.95:
            target_id = random.choice(inserted_ids)
            read_record(session, target_id)
        else:
            new_id = insert_record(session)
            inserted_ids.append(new_id)

def workload_f(session, inserted_ids, total_ops, start):
    
    for i in range(total_ops):
        target_id = random.choice(inserted_ids)
        if i % 1000 == 0:
            print(f"Executed {i} ops in {time.time() - start:.2f} seconds")
        if random.random() < 0.5:
            read_record(session, target_id)
        else:
            read_modify_write(session, target_id)
