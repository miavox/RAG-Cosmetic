import os
import json
from src.embeddings.multilingual_e5 import EmbeddingGenerator  # Import for embedding generation
from src.database.milvus_handler import MilvusHandler         # Import Milvus management class
from src.database.mongo_handler import MongoHandler           # Import MongoHandler for MongoDB connection
from src.database.schemas import ProductSchema                # Import ProductSchema for data validation
from dotenv import load_dotenv

load_dotenv()

class ProductIngestion:
    def __init__(self):
        # Initialize collection names from .env
        self.mongo_collection_name = os.getenv("MONGO_DB_NAME")
        self.milvus_collection_name = os.getenv("MILVUS_COLLECTION_NAME")

        # Initialize handlers
        self.embedding_generator = EmbeddingGenerator()
        self.milvus_handler = MilvusHandler(collection_name=self.milvus_collection_name, force_init=True, verbose=True)
        self.mongo_handler = MongoHandler(force_init=False)

    def ingest_product_data(self, json_file_path: str):
        """
        Reads product data from a JSON file and stores it in MongoDB and Milvus.

        Args:
            json_file_path (str): Path to the JSON file containing product data.
        """
        with open(json_file_path, "r", encoding="utf-8") as f:
            products = json.load(f)

        inserted_ids = []  # To store inserted MongoDB IDs

        for product_data in products:
            # Validate product data using schema
            try:
                product = ProductSchema(**product_data)
            except Exception as e:
                print(f"Validation error for product: {product_data.get('name', 'Unknown')} - {e}")
                continue  # Skip product if validation fails

            # Create a consistent `milvus_id` based on `product_id` or `name` (ensuring it’s a positive integer)
            milvus_id = product.milvus_id or abs(hash(product.name))  # Ensures `milvus_id` is positive

            # Prepare data for MongoDB
            product_dict = product.dict()
            product_dict["milvus_id"] = milvus_id

            # Insert product data into MongoDB before creating embedding
            try:
                inserted_id = self.mongo_handler.insert_one(product_dict, collection_name=self.mongo_collection_name)
                inserted_ids.append(inserted_id)
                print(f"Inserted document with ID `{inserted_id}` and milvus_id `{milvus_id}` into MongoDB.")
            except Exception as e:
                print(f"MongoDB insertion error for product: {product.name} - {e}")
                continue  # Skip product if MongoDB insertion fails

            # Generate and store embeddings in Milvus for each specified field
            for field_name, field_value in product.get_embedding_fields().items():
                if field_value:  # Skip if the field is None
                    embedding = self.embedding_generator.generate_embedding(field_value)
                    self.milvus_handler.save_embedding(milvus_id=milvus_id, field_name=field_name, embedding=embedding)
                    print(f"Saved embedding for product `{product.name}` - Field `{field_name}` in Milvus.")

        return inserted_ids