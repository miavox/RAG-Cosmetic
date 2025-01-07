import os
import json
from src.embeddings.multilingual_e5 import EmbeddingGenerator  # Import for embedding generation
from src.database.milvus_handler import MilvusHandler         # Import Milvus management class
from src.database.mongo_handler import MongoHandler           # Import MongoHandler for MongoDB connection
from src.database.schemas import ProductSchema                # Import ProductSchema for data validation
from src.database.ingest import ProductIngestion

json_file_path = "data/productsV7.json"  # Replace with the actual path to the JSON file

# Initialize the ProductIngestion class
product_ingestion = ProductIngestion()

# Ingest products
inserted_ids = product_ingestion.ingest_product_data(json_file_path=json_file_path)
print("All IDs inserted into MongoDB:", inserted_ids)