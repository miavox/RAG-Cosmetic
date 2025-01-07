import os
from src.embeddings.multilingual_e5 import EmbeddingGenerator  # Import lớp tạo embedding
from src.database.milvus_handler import MilvusHandler  # Import lớp quản lý Milvus

# Khởi tạo EmbeddingGenerator và MilvusHandler
embedding_generator = EmbeddingGenerator()
milvus_handler = MilvusHandler(collection_name="text_embeddings", verbose=True)

def search_in_milvus(query_text: str, field_name: str, limit: int = 10):
    """
    Tìm kiếm sản phẩm trong Milvus dựa trên embedding của văn bản truy vấn.

    Args:
        query_text (str): Văn bản truy vấn.
        field_name (str): Tên trường cần tìm kiếm (name, description, ingredients, instructions, comments).
        limit (int): Số lượng kết quả tối đa.

    Returns:
        list: Danh sách kết quả tìm kiếm.
    """
    print(f"Tạo embedding cho văn bản tìm kiếm: '{query_text}' trên trường '{field_name}'")
    query_embedding = embedding_generator.generate_embedding(query_text)
    
    # Truy vấn Milvus với embedding đã tạo
    print(f"Truy vấn Milvus với embedding, giới hạn kết quả: {limit}")
    results = milvus_handler.search(vector=query_embedding, field_name=field_name, limit=limit)

    # Xử lý và in ra kết quả
    for result in results:
        product_id = result.id
        distance = result.distance
        print(f"Sản phẩm ID: {product_id}, Độ tương đồng: {distance}")

    return results

if __name__ == "__main__":
    # Văn bản truy vấn và trường tìm kiếm
    query_text = "sản phẩm an toàn và dịu nhẹ trên mọi làn da ngay cả làn da nhạy cảm và da mụn"  # Văn bản truy vấn mẫu
    field_name = "ingredients"  # Trường để tìm kiếm, có thể là name, description, ingredients, instructions, hoặc comments
    
    # Thực hiện truy vấn
    search_results = search_in_milvus(query_text=query_text, field_name=field_name, limit=5)
