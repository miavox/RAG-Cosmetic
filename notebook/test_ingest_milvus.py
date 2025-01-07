import os
import json
from src.embeddings.multilingual_e5 import EmbeddingGenerator  # Import lớp tạo embedding
from src.database.milvus_handler import MilvusHandler  # Import lớp quản lý Milvus
from src.database.schemas import ProductSchema  # Import schema của sản phẩm

# Khởi tạo EmbeddingGenerator và MilvusHandler
embedding_generator = EmbeddingGenerator()
milvus_handler = MilvusHandler(collection_name="text_embeddings", force_init=True, verbose=True)

def ingest_product_data(json_file_path: str):
    """
    Đọc dữ liệu từ file JSON và lưu từng trường embedding vào Milvus.
    
    Args:
        json_file_path (str): Đường dẫn tới file JSON chứa dữ liệu sản phẩm.
    """
    with open(json_file_path, "r", encoding="utf-8") as f:
        products = json.load(f)

    for product_data in products:
        # Xác thực dữ liệu với schema
        product = ProductSchema(**product_data)
        
        # Lấy milvus_id từ product_id hoặc tạo mới nếu chưa có
        milvus_id = product.milvus_id or hash(product.name)  # Có thể dùng `hash` cho tên sản phẩm hoặc một cách khác

        # Duyệt qua từng trường cần tạo embedding
        for field_name, field_value in product.get_embedding_fields().items():
            if field_value:  # Bỏ qua trường nếu giá trị là None
                # Tạo embedding cho giá trị của trường
                embedding = embedding_generator.generate_embedding(field_value)
                
                # Lưu embedding vào Milvus cho trường cụ thể
                milvus_handler.save_embedding(milvus_id=milvus_id, field_name=field_name, embedding=embedding)
                print(f"Đã lưu embedding cho sản phẩm `{product.name}` - Trường `{field_name}`.")

if __name__ == "__main__":
    # Đường dẫn tới file JSON chứa dữ liệu sản phẩm
    json_file_path = "data/productsV7.json"
    ingest_product_data(json_file_path=json_file_path)
