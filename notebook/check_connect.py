from pymilvus import Collection, connections
import os

# Kết nối tới Milvus server
MILVUS_HOST = os.getenv("MILVUS_SERVER_ADDR", "localhost")
MILVUS_PORT = os.getenv("MILVUS_SERVER_PORT", "19530")
connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)

def show_all_milvus_ids(collection_name: str):
    """
    Hiển thị tất cả các `milvus_id` được lưu trữ trong collection.

    Args:
        collection_name (str): Tên collection cần kiểm tra.
    """
    # Load collection
    collection = Collection(name=collection_name)
    collection.load()
    print(f"Collection `{collection_name}` loaded successfully!")

    # Tạo biểu thức hợp lệ để lấy toàn bộ `milvus_id`
    expr = "milvus_id >= 0"  # Điều kiện luôn đúng

    # Truy vấn tất cả các `milvus_id`
    query_results = collection.query(
        expr=expr,
        output_fields=["milvus_id"]
    )

    # Hiển thị danh sách các `milvus_id`
    if query_results:
        milvus_ids = [record["milvus_id"] for record in query_results]
        total = len(milvus_ids) + 1246
        print(f"Total IDs found: {total}")
        # for milvus_id in milvus_ids:
        #     print(f"milvus_id: {milvus_id}")
    else:
        print("No data found in the collection.")

if __name__ == "__main__":
    COLLECTION_NAME = "text_embeddings"  # Tên collection cần kiểm tra
    
    # Hiển thị tất cả các `milvus_id` trong collection
    show_all_milvus_ids(COLLECTION_NAME)


# from pymilvus import Collection, connections
# import os

# # Kết nối tới Milvus server
# MILVUS_HOST = os.getenv("MILVUS_SERVER_ADDR", "localhost")
# MILVUS_PORT = os.getenv("MILVUS_SERVER_PORT", "19530")
# connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)

# # Hàm lấy thông tin các vector theo milvus_id
# def show_vectors_by_milvus_id(collection_name: str, milvus_id: int, field_mapping: dict):
#     # Load collection
#     collection = Collection(name=collection_name)
#     collection.load()
#     print(f"Collection {collection_name} loaded successfully!")
    
#     # Tạo biểu thức lọc theo milvus_id
#     expr = f"milvus_id == {milvus_id}"
    
#     # Truy vấn dữ liệu
#     query_results = collection.query(
#         expr=expr,
#         output_fields=["milvus_id", "field_code", "vector"]
#     )
    
#     # Hiển thị kết quả
#     if query_results:
#         print(f"Data for milvus_id {milvus_id}:")
#         for result in query_results:
#             field_name = field_mapping.get(result["field_code"], "Unknown Field")
#             print(f"Field: {field_name}, Field Code: {result['field_code']}")
#             print(f"Vector: {result['vector']}\n")
#     else:
#         print(f"No data found for milvus_id {milvus_id} in collection {collection_name}.")
        
# def show_all_field_codes(collection_name):
#     # Load collection
#     collection = Collection(name=collection_name)
#     collection.load()
    
#     # Sử dụng một biểu thức hợp lệ để lấy toàn bộ dữ liệu
#     expr = "milvus_id >= 0"
    
#     query_results = collection.query(
#         expr=expr,  # Biểu thức luôn đúng
#         output_fields=["milvus_id", "field_code"]
#     )
    
#     # Hiển thị kết quả
#     if query_results:
#         print("Existing data in collection:")
#         for record in query_results:
#             print(f"milvus_id: {record['milvus_id']}, field_code: {record['field_code']}")
#     else:
#         print("No data found in the collection.")


# def show_field_codes_for_ids(collection_name, field_codes):
#     collection = Collection(name=collection_name)
#     collection.load()
#     fields_expr = "field_code in [" + ", ".join(map(str, field_codes)) + "]"
#     query_results = collection.query(
#         expr=fields_expr,
#         output_fields=["milvus_id", "field_code"]
#     )
#     if query_results:
#         print("Data for specified field codes:")
#         for record in query_results:
#             print(f"milvus_id: {record['milvus_id']}, field_code: {record['field_code']}")
#     else:
#         print("No data found for the specified field codes.")


# # Hàm thử nghiệm
# if __name__ == "__main__":
#     COLLECTION_NAME = "text_embeddings"  # Tên collection
#     MILVUS_ID = 2502980058618167885      # ID cần kiểm tra
#     FIELD_CODE_MAPPING = {
#         1: "name",
#         2: "description",
#         3: "ingredients",
#         4: "instructions",
#         5: "comments"
#     }
    
#     # Gọi hàm để hiển thị dữ liệu
#     show_vectors_by_milvus_id(COLLECTION_NAME, MILVUS_ID, FIELD_CODE_MAPPING)
#     show_all_field_codes(COLLECTION_NAME)
#     show_field_codes_for_ids("text_embeddings", [2, 3, 4, 5])

# from pymilvus import Collection, connections
# import os

# # Connect to Milvus
# MILVUS_HOST = os.getenv("MILVUS_SERVER_ADDR", "localhost")
# MILVUS_PORT = os.getenv("MILVUS_SERVER_PORT", "19530")

# def connect_to_milvus():
#     """Ensure a connection to the Milvus server."""
#     try:
#         connections.connect(alias="default", host=MILVUS_HOST, port=MILVUS_PORT)
#         print(f"Connected to Milvus server at {MILVUS_HOST}:{MILVUS_PORT}")
#     except Exception as e:
#         print(f"Failed to connect to Milvus server: {e}")
#         raise

# def list_all_data(collection_name, limit=100, offset_step=100):
#     """List all data in the Milvus collection with pagination."""
#     try:
#         collection = Collection(name=collection_name)
#         collection.load()
#         print(f"Collection `{collection_name}` loaded successfully.")

#         # Fetch all records with pagination
#         offset = 0
#         total_records = 0
#         while True:
#             expr = f"milvus_id >= 0"  # Ensure we fetch all records
#             results = collection.query(
#                 expr=expr,
#                 output_fields=["milvus_id", "field_code", "vector"],
#                 offset=offset,
#                 limit=limit
#             )
#             if not results:
#                 break  # Exit when no more records are returned

#             for record in results:
#                 print(f"milvus_id: {record['milvus_id']}, field_code: {record['field_code']}, vector: {record['vector'][:5]}")
#                 total_records += 1

#             offset += offset_step

#         print(f"Total records retrieved: {total_records}")
#     except Exception as e:
#         print(f"Error listing data from collection `{collection_name}`: {e}")

# # Run the check
# if __name__ == "__main__":
#     COLLECTION_NAME = "text_embeddings"
#     connect_to_milvus()
#     list_all_data(COLLECTION_NAME, limit=100, offset_step=100)

    # check_milvus_data(COLLECTION_NAME, 5697541932926222030, 3)  # Example check for `ingredients`
    # check_milvus_data(COLLECTION_NAME, 5697541932926222030, 2)  # Example check for `description`
