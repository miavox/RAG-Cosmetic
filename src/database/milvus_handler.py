import os
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, list_collections
from dotenv import load_dotenv

load_dotenv()

# Define dimension of embeddings for fields
feature_registry = {"e5_large": 1024}

class MilvusHandler:
    # Mapping `field_code` for different fields
    FIELD_CODE_MAPPING = {
        "name": 1,
        "description": 2,
        "ingredients": 3,
        "instructions": 4,
        "comments": 5
    }

    def __init__(self, collection_name: str, force_init: bool = False, verbose: bool = False):
        self.collection_name = collection_name
        self.host = os.getenv("MILVUS_SERVER_ADDR")
        self.port = os.getenv("MILVUS_SERVER_PORT")
        self.verbose = verbose
        self.feature_dim = feature_registry["e5_large"]

        # Connect to Milvus
        connections.connect(alias="default", host=self.host, port=self.port)

        # Initialize collection if needed
        if force_init or self.collection_name not in list_collections():
            self.collection = self._initialize_collection(force_init=force_init)
        else:
            self.collection = Collection(name=self.collection_name)

        # Load collection into memory
        self.collection.load()

    def _initialize_collection(self, force_init: bool = False):
        # Define schema with milvus_id, field_code, and vector embedding
        fields = [
            FieldSchema(name="milvus_id", dtype=DataType.INT64, is_primary=True),
            FieldSchema(name="field_code", dtype=DataType.INT64),  # Code for field type
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.feature_dim)
        ]
        schema = CollectionSchema(fields=fields, enable_dynamic_field=False)
        index_params = {"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 1024}}

        # Drop collection if force_init is True and collection exists
        if force_init and self.collection_name in list_collections():
            Collection(name=self.collection_name).drop()

        # Create new collection
        collection = Collection(name=self.collection_name, schema=schema)
        collection.create_index("vector", index_params)
        
        if self.verbose:
            print(f"Successfully initialized new collection: `{self.collection_name}`")
        
        return collection

    def save_embedding(self, milvus_id: int, field_name: str, embedding: list):
        # Determine field_code based on the field name
        field_code = self.FIELD_CODE_MAPPING.get(field_name)
        if not field_code:
            raise ValueError(f"Invalid field name '{field_name}'. Please use one of {list(self.FIELD_CODE_MAPPING.keys())}.")

        # Save embedding with milvus_id and field_code
        data_to_insert = [
            [milvus_id],
            [field_code],
            [embedding]
        ]
        self.collection.insert(data=data_to_insert)
        if self.verbose:
            print(f"Inserted embedding for milvus_id `{milvus_id}`, field `{field_name}` with field_code `{field_code}`.")

    def search(self, vector: list, field_name: str, limit: int = 5, expr: str = None):
        # Get field code from field name
        field_code = self.FIELD_CODE_MAPPING.get(field_name)
        if not field_code:
            raise ValueError(f"Invalid field name '{field_name}'.")

        # Convert milvus_ids to valid format (if provided in expr)
        if "in" in expr:
            # Ensure expr is properly formatted with integers
            expr = expr.replace("'", "")  # Remove quotes if any

        # Define search parameters
        search_params = {"metric_type": "L2", "params": {"nprobe": 256}}

        # Log the expression and parameters
        if self.verbose:
            print(f"Searching in Milvus with expression: `{expr}` and limit: {limit}")

        # Perform search
        try:
            results = self.collection.search(
                data=[vector],
                anns_field="vector",
                limit=limit,
                param=search_params,
                expr=expr,
                output_fields=["milvus_id", "field_code"]
            )
        except Exception as e:
            if self.verbose:
                print(f"Milvus search failed: {e}")
            raise e

        # Log results
        if self.verbose and results:
            print(f"Milvus search returned {len(results[0])} results.")
        elif self.verbose:
            print("Milvus search returned no results.")

        return results[0] if results else []
