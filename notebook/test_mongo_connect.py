from src.database.mongo_handler import MongoHandler

mongo_handler = MongoHandler()
print(mongo_handler.check_connection())