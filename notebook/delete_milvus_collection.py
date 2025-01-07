import os
from pymilvus import connections, Collection

# Lấy thông tin kết nối từ biến môi trường
milvus_host = os.getenv("MILVUS_SERVER_ADDR", "localhost")
milvus_port = os.getenv("MILVUS_SERVER_PORT", "19530")
collection_name = os.getenv("MILVUS_COLLECTION_NAME", "text_embeddings")

# Kết nối đến Milvus server
connections.connect("default", host=milvus_host, port=milvus_port)

# Khởi tạo collection
collection = Collection(collection_name)

# Xóa toàn bộ dữ liệu bằng cách thả collection vào một partition mới
collection.release()  # Giải phóng bộ nhớ
collection.drop()     # Thả toàn bộ vector
