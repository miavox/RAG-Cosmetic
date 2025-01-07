from src.database.mongo_handler import MongoHandler

# Khởi tạo MongoHandler
mongo_handler = MongoHandler()

# Gọi phương thức drop_database để xóa toàn bộ cơ sở dữ liệu
mongo_handler.drop_database()
