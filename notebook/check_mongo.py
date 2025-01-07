from src.database.mongo_handler import MongoHandler  # Đảm bảo MongoHandler đã được cấu hình chính xác
import os

# Khởi tạo MongoHandler
mongo_handler = MongoHandler(force_init=False)

def check_product_data():
    """
    Truy vấn tất cả các sản phẩm trong MongoDB và hiển thị thông tin chi tiết.
    """
    # collection_name = os.getenv("MONGO_DB_NAME")
    products = mongo_handler.query(collection_name="rag_cosmetic")
    product_count = len(products) if products else 0
    print(f"Tổng số sản phẩm trong MongoDB: {product_count}")

    for product in products[:3]:
        print("Sản phẩm:")
        print(f" - ID: {product.get('_id')}")
        print(f" - Milvus ID: {product.get('milvus_id')}")
        print(f" - Tên: {product.get('name')}")
        print(f" - Giá: {product.get('price')}")
        print(f" - URL: {product.get('link')}")
        print(f" - Ảnh: {product.get('img')}")
        print(f" - Mô tả: {product.get('description')}")
        print(f" - Thành phần: {product.get('ingredients')}")
        print(f" - Hướng dẫn: {product.get('instructions')}")
        print(f" - Đặc điểm: {product.get('specifications')}")
        print(f" - Loại da: {product.get('skin_type')}")
        print(f" - Đánh giá: {product.get('rating')}")
        print(f" - Bình luận: {product.get('comments')}")
        print(f" - Màu sắc: {product.get('color')}")
        print(f" - Trạng thái kho: {product.get('stock')}")
        print(f" - Thể tích/Trọng lượng: {product.get('volume_weight')}")
        print(f" - Thương hiệu: {product.get('brand')}")
        print("----------")

if __name__ == "__main__":
    check_product_data()
