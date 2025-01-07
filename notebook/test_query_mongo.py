from src.sort_mongo.sort import MongoSort

# Example usage
task_data = {
    'product_type': ['sữa rửa mặt', 'Nước Hoa Hồng'], 
    'budget': '<500000', 
    'special_requirements': {
        'popularity': None, 
        'ingredients': ['tràm trà', 'null'], 
        'instructions': ['hỗ trợ kiềm dầu, làm sạch sâu và thông thoáng lỗ chân lông', 'giúp thông thoáng và giảm bít tắc, hỗ trợ se khít lỗ chân lông'], 
        'description': ['dành cho da dầu mụn', 'Dành Cho Da Mụn'], 
        'skin_type': 'Da dầu/Hỗn hợp dầu', 
        'skin_tone': None, 
        'size': None, 
        'sale': None, 
        'category': ['Chăm Sóc Da Mặt / Làm Sạch Da / Sữa Rửa Mặt', 'Chăm Sóc Da Mặt / Làm Sạch Da / Toner / Nước Cân Bằng Da'], 
        'brand': None, 
        'name': None, 
        'color_code': None
        }
    }


extracted_data = {
    "product_type": ["sữa rửa mặt"],
    "budget": "<300000",
    "special_requirements": {
        "popularity": None,
        "ingredients": ["tràm trà"],
        "instructions": ["hỗ trợ kiềm dầu", "làm sạch sâu", "thông thoáng lỗ chân lông"],
        "description": None,
        "skin_type": "Da dầu/Hỗn hợp dầu",
        "skin_tone": None,
        "size": None,
        "sale": None,
        "category": ["Chăm Sóc Da Mặt / Làm Sạch Da / Sữa Rửa Mặt"],
        "brand": None,
        "name": None,
        "color_code": [None]
    }
}

product_search = MongoSort(task_data)
print(product_search.run())