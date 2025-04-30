# scyllaDB-YCSB
Test repository for scyllaDB on YCSB workloads
Repo install: curl -sSf get.scylladb.com/server | sudo bash

Docker Setup as docker needed for running ScyllaDB instance:
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo docker run hello-world

Download image of ScyllaDB
sudo docker pull scylladb/scylla

To start a one-node ScyllaDB instance:
sudo docker run --name scylla -d scylladb/scylla

sudo docker run --name scylla -d -p 9042:9042 scylladb/scylla

To list all Docker containers running:
sudo docker ps -a

To remove a Docker container:
sudo docker rm scylla

To close a docker container 
sudo docker stop scylla

ScyllaDB installation command:
sudo curl -sSf get.scylladb.com/server | sudo bash

ScyllaDb status: To verify that the cluster is up and running:
sudo docker exec -it scylla nodetool status

Run ScyllaDB on one node and then for running on second node in cluster run
sudo docker run --name some-scylla -d scylladb/scylla - run on first node
sudo docker run --name some-scylla2 -d scylladb/scylla --seeds="$(sudo docker inspect --format='{{ .NetworkSettings.IPAddress }}' some-scylla)" - run on second node
To check status of scylladb cluster: sudo docker exec -it some-scylla nodetool status

Run first 2 docker containers and then run main.py using this in background:
sudo python3 main.py --containers some-scylla some-scylla2 &>withoutcomapction-5m-inserts-1mops.txt &

sudo usermod -aG docker smitshah
Add the user to the docker group

Check existing records in a node of cluster!
docker exec -it some-scylla bash
cqlsh
USE ycsb;
SELECT * FROM usertable LIMIT 10;


TODO Tasks:
ScyllaDB compaction strategies experiments
Use cassandra-stress package to stress test on different read/write/read-write mix workloads
Use perfstat, nodetool , vmstat to analyze
Test against YCSB workloads.


## Performance Analysis:
Run on the following workloads:
Read 50% Update 50%
Read 100%
Write 100%
Update 100%

All ycsb workloads except Scan.

totalOps:       1K, 10K, 100K 
totalUniqueKeys:10K, 100K
number of nodes: 1,3,5
compaction: 'SizeTieredCompactionStrategy', 'LeveledCompactionStrategy', 'IncrementalCompactionStrategy' (Only for enterprise versions), 'TimeWindowCompactionStragety'

## Things to be passed as arguments to the client:
insert_keys_count = 50000
total_ops = 10000
compaction
  
    if compaction == 'SizeTieredCompactionStrategy':
        compaction_settings = {
            'class': compaction,
            'bucket_high': factor,
            'bucket_low': factor,
            'min_sstable_size': min_sstable_size,
            'min_threshold': num_sstables,
            'max_threshold': num_sstables
        }
    elif compaction == 'LeveledCompactionStrategy':
        {
        'class' : 'LeveledCompactionStrategy',
        'sstable_size_in_mb' : int}
        
    elif compaction == 'TimeWindowCompactionStragety':
      {
  'class' : 'TimeWindowCompactionStrategy',
  'compaction_window_unit' : string,
  'compaction_window_size' : int,
  'expired_sstable_check_frequency_seconds' : int,
  'min_threshold' : num_sstables,
  'max_threshold' : num_sstables}


References: 
Cassandra paper: https://www.cs.cornell.edu/projects/ladis2009/papers/lakshman-ladis2009.pdf
Cassandra stress: https://cassandra.apache.org/doc/stable/cassandra/tools/cassandra_stress.html
Cassandra vs ScyllaDb for IOT workloads: https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7945437
Interview Radio with CTO of ScyllaDB: https://www.computer.org/csdl/magazine/so/2019/04/08738153/1aW6mIzPvos
White paper Design COnsiderations: ScyllaDB : https://toidiu.com/reads/Building_the_Real-Time_Big_Data_Database-_Seven_Design_Principles_behind_Scylla.pdf
ScyllaDB architecture: https://docs.scylladb.com/manual/stable/architecture/index.html

ScyllaDB Compaction Strategy in Practice usig cqlsh:  https://opensource.docs.scylladb.com/stable/cql/ddl.html#create-table-statement
https://opensource.docs.scylladb.com/stable/cql/compaction.html
ScyllaDB Configuration files : https://opensource.docs.scylladb.com/stable/operating-scylla/admin.html