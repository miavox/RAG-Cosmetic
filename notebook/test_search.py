from src.embeddings.multilingual_e5 import EmbeddingGenerator
from src.database.milvus_handler import MilvusHandler
import numpy as np

class QueryProcessor:
    def __init__(self, embedding_generator: EmbeddingGenerator, milvus_handler: MilvusHandler):
        """
        Xử lý embedding và tìm kiếm trên Milvus.
        """
        self.embedding_generator = embedding_generator
        self.milvus_handler = milvus_handler

    def generate_query_embeddings(self, query: dict):
        """
        Tạo embeddings từ truy vấn người dùng theo từng trường.

        Args:
            query (dict): Truy vấn người dùng, dạng {"field_name": "query text"}.

        Returns:
            dict: Embeddings theo trường, {"field_name": embedding_vector}.
        """
        embeddings = {}
        for field_name, query_text in query.items():
            if query_text:
                embedding = self.embedding_generator.generate_embedding(query_text)
                embeddings[field_name] = embedding
        return embeddings

    def search_on_milvus(self, query: dict, mongo_ids: list, fields: list, limit: int = 5):
        """
        Thực hiện tìm kiếm trên Milvus với truy vấn được nhúng.

        Args:
            query (dict): Truy vấn người dùng, dạng {"field_name": "query text"}.
            mongo_ids (list): Danh sách `milvus_id` từ MongoDB.
            fields (list): Danh sách các trường cần tìm kiếm.
            limit (int): Số kết quả trả về mỗi trường.

        Returns:
            list: Kết quả tìm kiếm sắp xếp theo average similarity.
        """
        # Tạo embedding từ truy vấn
        query_embeddings = self.generate_query_embeddings(query)

        all_results = []
        for field_name, vector in query_embeddings.items():
            if field_name in fields:
                # Tìm kiếm trên Milvus theo từng trường
                results = self.milvus_handler.search(
                    vector=vector,
                    field_name=field_name,
                    limit=limit,
                    expr=f"milvus_id in {mongo_ids}"
                )
                all_results.append(results)

        # Tính toán similarity trung bình
        return self.calculate_similarity(all_results)

    def calculate_similarity(self, results):
        """
        Tính similarity trung bình cho mỗi `milvus_id`.

        Args:
            results (list): Kết quả từ Milvus.

        Returns:
            list: Danh sách `milvus_id` và average similarity.
        """
        similarities = {}
        for result in results:
            for hit in result:
                milvus_id = hit.id
                distance = hit.distance
                similarity = 1 / (1 + distance)  # Chuyển đổi từ L2 distance sang similarity
                
                if milvus_id not in similarities:
                    similarities[milvus_id] = []
                similarities[milvus_id].append(similarity)

        # Tính average similarity
        average_similarities = [
            {"milvus_id": milvus_id, "avg_similarity": np.mean(scores)}
            for milvus_id, scores in similarities.items()
        ]

        # Sắp xếp giảm dần theo average similarity
        sorted_results = sorted(average_similarities, key=lambda x: x["avg_similarity"], reverse=True)
        return sorted_results

# Giả định truy vấn người dùng
user_query = {
    "ingredients": "giúp làm dịu, nuôi dưỡng, củng cố hàng rào da",
    "description": "loại bỏ bụi bẩn"
}

# MongoDB trả về
mongo_result = {'combos': [['5697541932926222030'], ['8616980345624713595']], 'result': True}
milvus_ids = [milvus_id for combo in mongo_result["combos"] for milvus_id in combo]

# Khởi tạo Embedding Generator và Milvus Handler
embedding_generator = EmbeddingGenerator()
milvus_handler = MilvusHandler(collection_name="text_embeddings", force_init=False, verbose=True)

# Xử lý và tìm kiếm
query_processor = QueryProcessor(embedding_generator, milvus_handler)
fields = ["ingredients", "description"]
results = query_processor.search_on_milvus(user_query, milvus_ids, fields, limit=5)

# Hiển thị kết quả
print("Kết quả tìm kiếm sắp xếp theo average similarity:")
for result in results:
    print(result)
