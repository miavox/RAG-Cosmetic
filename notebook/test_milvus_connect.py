import os
from pymilvus import connections

milvus_host = os.getenv("MILVUS_SERVER_ADDR") 
milvus_port = os.getenv("MILVUS_SERVER_PORT")

try:
    # Connect to Milvus
    connections.connect(host=milvus_host, port=milvus_port)
    print("Connected to Milvus server at:", milvus_host, "port:", milvus_port)
except Exception as e:
    # Print error message if connection fails
    print("Cannot connect to Milvus server. Error:", e)