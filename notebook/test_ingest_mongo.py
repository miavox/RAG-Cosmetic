import os
import json
from src.database.schemas import ProductSchema  # Import ProductSchema để xác thực dữ liệu
from src.database.mongo_handler import MongoHandler  # Import MongoHandler để kết nối và tương tác với MongoDB



def insert_products_from_json(json_file_path, milvus_id=None):
    """
    Xác thực dữ liệu từ file JSON và chèn vào MongoDB.
    
    Args:
        json_file_path (str): Đường dẫn đến file JSON chứa dữ liệu sản phẩm.
        milvus_id (str): ID liên kết với Milvus, mặc định là None.
        
    Returns:
        list: Danh sách các ID của tài liệu đã chèn trong MongoDB.
    """
    # Khởi tạo MongoHandler
    mongo_handler = MongoHandler(force_init=False)
    inserted_ids = []

    # Đọc dữ liệu từ file JSON
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Kiểm tra nếu dữ liệu là danh sách, xử lý từng mục
    if isinstance(data, list):
        for item in data:
            try:
                validated_data = ProductSchema(**item)
                data_with_milvus_id = validated_data.dict()
                data_with_milvus_id["milvus_id"] = milvus_id
                inserted_id = mongo_handler.insert_one(data_with_milvus_id, collection_name="product")
                inserted_ids.append(inserted_id)
                print(f"Inserted document with ID `{inserted_id}` and milvus_id `{milvus_id}` into MongoDB.")
            except Exception as e:
                print(f"Validation error for item: {item['name']} - {e}")
    else:
        # Nếu không phải là danh sách, chỉ xử lý một mục duy nhất
        try:
            validated_data = ProductSchema(**data)
            data_with_milvus_id = validated_data.dict()
            data_with_milvus_id["milvus_id"] = milvus_id
            inserted_id = mongo_handler.insert_one(data_with_milvus_id, collection_name="product")
            inserted_ids.append(inserted_id)
            print(f"Inserted document with ID `{inserted_id}` and milvus_id `{milvus_id}` into MongoDB.")
        except Exception as e:
            print(f"Validation error: {e}")

    return inserted_ids

# Đường dẫn tới file JSON và ID Milvus (nếu có)
json_file_path = "data/productsV7.json"  # Thay thế bằng đường dẫn thực tế
milvus_id = "example_milvus_id_123"  # ID liên kết với Milvus (nếu có)

# Gọi hàm để chèn sản phẩm từ JSON
inserted_ids = insert_products_from_json(json_file_path, milvus_id=milvus_id)
print("Inserted document IDs:", inserted_ids)