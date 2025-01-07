import os
import pymongo
from pymongo.errors import ConnectionFailure
from urllib.parse import quote_plus
from datetime import datetime
import json
import copy
from dotenv import load_dotenv

load_dotenv()

class MongoHandler:
    def __init__(self, force_init: bool = False):
        """
        Khởi tạo kết nối đến MongoDB và thiết lập các collection cho sản phẩm và kết quả tìm kiếm.

        Biến Môi Trường:
            MONGO_PRODUCT_COLLECTION: Tên của collection cho sản phẩm.
            MONGO_SEARCH_RESULT_COLLECTION: Tên của collection cho kết quả tìm kiếm.
            MONGO_DB_NAME: Tên của cơ sở dữ liệu.
            MONGO_USRNAME: Tên người dùng MongoDB.
            MONGO_PASSWD: Mật khẩu MongoDB.
            MONGO_SERVER_ADDR: Địa chỉ máy chủ MongoDB (vd: localhost:27017).
        """
        # Lấy thông tin từ file .env
        self.product_collection_name = os.getenv("MONGO_PRODUCT_COLLECTION")
        self.search_result_collection_name = os.getenv("MONGO_SEARCH_RESULT_COLLECTION")
        
        db_name = os.getenv("MONGO_DB_NAME")
        usrname = quote_plus(os.getenv("MONGO_USRNAME"))
        passwd = quote_plus(os.getenv("MONGO_PASSWD"))
        server_address = os.getenv("MONGO_SERVER_ADDR")
        mongo_uri = f"mongodb://{usrname}:{passwd}@{server_address}"
        
        # Kết nối đến MongoDB
        client = pymongo.MongoClient(mongo_uri)
        self.db = client[db_name]

        # Khởi tạo các collection
        self.product_collection = self.db[self.product_collection_name]
        self.search_result_collection = self.db[self.search_result_collection_name]
        
        # Nếu force_init=True, xóa và khởi tạo lại các collection
        if force_init:
            self.product_collection.drop()
            self.search_result_collection.drop()
            print(f"MONGODB: Forcedly Initialized Collections: `{self.product_collection_name}` and `{self.search_result_collection_name}`")
        else:
            print(f"MONGODB: Loaded Existing Collections: `{self.product_collection_name}` and `{self.search_result_collection_name}`")

    def insert_one(self, data: dict, collection_name: str = "product"):
        """
        Chèn một tài liệu vào MongoDB với timestamp hiện tại.
        
        Args:
            data (dict): Dữ liệu để chèn vào MongoDB.
            collection_name (str): Tên collection để chèn dữ liệu ("product" hoặc "search_result").
            
        Returns:
            inserted_id: ID của tài liệu đã chèn.
        """
        collection = self.product_collection if collection_name == "product" else self.search_result_collection
        insert_data = copy.deepcopy(data)
        insert_data["time"] = datetime.utcnow()
        result = collection.insert_one(insert_data)
        return result.inserted_id

    def insert_from_json_file(self, json_file_path: str, milvus_id=None):
        """
        Đọc dữ liệu từ file JSON và chèn vào MongoDB với collection sản phẩm.
        
        Args:
            json_file_path (str): Đường dẫn tới file JSON chứa dữ liệu sản phẩm.
            milvus_id (str): ID liên kết với Milvus, mặc định là None.
        
        Returns:
            inserted_id: ID của tài liệu vừa chèn trong MongoDB.
        """
        # Đọc dữ liệu từ file JSON
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Thêm 'milvus_id' nếu được cung cấp
        data["milvus_id"] = milvus_id if milvus_id else None

        # Chèn dữ liệu vào MongoDB
        inserted_id = self.insert_one(data, collection_name="product")
        print(f"Inserted document with ID `{inserted_id}` and milvus_id `{milvus_id}` into MongoDB collection `{self.product_collection_name}`.")
        return inserted_id

    def bulk_insert(self, data: list, collection_name: str = "product"):
        """
        Chèn hàng loạt tài liệu vào MongoDB, mặc định vào collection sản phẩm.
        
        Args:
            data (list): Danh sách các tài liệu (dict) để chèn.
            collection_name (str): Tên collection để chèn dữ liệu ("product" hoặc "search_result").
        
        Returns:
            inserted_ids: Danh sách các ID của tài liệu đã chèn.
        """
        collection = self.product_collection if collection_name == "product" else self.search_result_collection
        for item in data:
            item["time"] = datetime.utcnow()
        result = collection.insert_many(data)
        return result.inserted_ids

    def query(self, query: dict = {}, collection_name: str = "product"):
        """
        Truy vấn MongoDB với điều kiện truy vấn cụ thể từ một collection.
        
        Args:
            query (dict): Truy vấn MongoDB.
            collection_name (str): Tên collection để truy vấn ("product" hoặc "search_result").
            
        Returns:
            list: Danh sách các tài liệu phù hợp với truy vấn.
        """
        collection = self.product_collection if collection_name == "product" else self.search_result_collection
        return list(collection.find(query))

    def update_one(self, filter_query: dict, update: dict, collection_name: str = "product"):
        """
        Cập nhật một tài liệu duy nhất trong MongoDB dựa trên filter_query.
        
        Args:
            filter_query (dict): Điều kiện lọc để tìm tài liệu cần cập nhật.
            update (dict): Dữ liệu cập nhật.
            collection_name (str): Tên collection để cập nhật ("product" hoặc "search_result").
            
        Returns:
            modified_count: Số lượng tài liệu đã cập nhật.
        """
        collection = self.product_collection if collection_name == "product" else self.search_result_collection
        result = collection.update_one(filter_query, {"$set": update})
        return result.modified_count
    
    def check_connection(self):
        """
        Kiểm tra kết nối đến MongoDB bằng cách thực hiện lệnh `ping`.

        Returns:
            str: Thông báo kết quả kết nối.
        """
        try:
            # Thực hiện lệnh ping để kiểm tra kết nối
            self.db.command("ping")
            return "Kết nối thành công đến MongoDB!"
        except ConnectionFailure as e:
            return f"Không thể kết nối đến MongoDB. Lỗi: {e}"
        
    def drop_database(self):
        """
        Xóa toàn bộ cơ sở dữ liệu đã được chỉ định trong MongoDB.
        """
        try:
            # Xóa toàn bộ cơ sở dữ liệu
            self.db.client.drop_database(self.db.name)
            print(f"MONGODB: Database `{self.db.name}` đã bị xóa thành công.")
        except Exception as e:
            print(f"Lỗi khi xóa database `{self.db.name}`. Lỗi: {e}")