from src.database.search import ProductSearch
import time
from src.utils import adjust_and_ensure_json, generate_query_texts_fields_with_brand_check, generate_query_texts_fields
# Define MongoDB filter
# mongo_filter = {
#     'product_type': ['sữa rửa mặt'], 
#     'budget': '<500000', 
#     'special_requirements': {
#         'popularity': None, 
#         'ingredients': ['tràm trà'], 
#         'instructions': ['hỗ trợ kiềm dầu, làm sạch sâu và thông thoáng lỗ chân lông'], 
#         'description': ['dành cho da dầu mụn'], 
#         'skin_type': 'Da dầu/Hỗn hợp dầu', 
#         'skin_tone': None, 
#         'size': [None], 
#         'sale': None, 
#         'category': ['Chăm Sóc Da Mặt / Làm Sạch Da / Sữa Rửa Mặt'], 
#         'brand': [None], 
#         'name': None, 
#         'color_code': [None]
#     }
# }

# mongo_filter = {'budget': "<350000", 
#                 'special_requirements': {
#                     'popularity': None, 
#                     'ingredients': ['làm sạch đến 99% lớp trang điểm, 70% mascara, bã nhờn, bụi mịn PM2.5'], 
#                     'instructions': None, 
#                     'description': ['nước tẩy trang cho da dầu'], 
#                     'skin_type': ['Da dầu/Hỗn hợp dầu'], 
#                     'skin_tone': [None], 
#                     'size': [None], 
#                     'sale': None, 
#                     'category': ['Chăm Sóc Da Mặt / Làm Sạch Da / Sữa Rửa Mặt'], 
#                     'brand': [None], 
#                     'name': [None], 
#                     'color_code': [None]
#                     }
#                 }

mongo_filter = {
    'budget': None, 
    'sale': False, 
    'comparison': False, 
    'special_requirements': {
        'popularity': [None], 
        'ingredients': [None], 
        'instructions': [None], 
        'description': [None], 
        'skin_type': [None], 
        'skin_tone': [None], 
        'size': [None], 
        'category': ['Chăm Sóc Tóc Và Da Đầu / Dầu Gội Và Dầu Xả / Dầu Gội'], 
        'brand': [None], 
        'name': ['dầu gội đầu trị gàu']
        }
    }

# Define query parameters (multiple fields)
# query_texts_fields = [
#     [
#         ("chứa vitamin C", "ingredients"),
#         ("Kem Nền Mịn Nhẹ Kiềm Dầu Chống Nắng", "description")
#     ],
#     []
# ]

mongo_filter = (mongo_filter)
print(mongo_filter)

if mongo_filter['comparison'] and len(mongo_filter['special_requirements']['brand']) > 1:
    query_texts_fields = generate_query_texts_fields_with_brand_check(mongo_filter)
    print(query_texts_fields)
else:
    query_texts_fields = generate_query_texts_fields(mongo_filter)
    print(query_texts_fields)

product_search = ProductSearch()
results = product_search.search_combo_products(query_texts_fields, mongo_filter)
print(results)