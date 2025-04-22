from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
cluster = Cluster(
    contact_points=[
        "localhost",
    ],
    auth_provider=PlainTextAuthProvider(username='scylla', password='your-awesome-password')
)
print('Cluster', cluster)