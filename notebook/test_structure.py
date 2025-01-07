


# Test case 1
mongo_filter_1 = {
    'budget': '<350000',
    'special_requirements': {
        'popularity': None,
        'ingredients': ['làm sạch đến 99% lớp trang điểm, 70% mascara, bã nhờn, bụi mịn PM2.5'],
        'instructions': None,
        'description': ['nước tẩy trang cho da dầu'],
        'skin_type': ['Da dầu/Hỗn hợp dầu'],
        'skin_tone': [None],
        'size': [None],
        'sale': None,
        'category': ['Chăm Sóc Da Mặt / Làm Sạch Da / Tẩy Trang Mặt'],
        'brand': [None],
        'name': [None],
        'color_code': [None]
    }
}

# Test case 2
mongo_filter_2 = {
    'product_type': ['sữa rửa mặt', 'Nước Hoa Hồng'], 
    'budget': '<500000', 
    'special_requirements': {
        'popularity': None, 
        'ingredients': ['tràm trà', None], 
        'instructions': ['hỗ trợ kiềm dầu, làm sạch sâu và thông thoáng lỗ chân lông', 'giúp thông thoáng và giảm bít tắc, hỗ trợ se khít lỗ chân lông'], 
        'description': ['dành cho da dầu mụn', 'Dành Cho Da Mụn'], 
        'skin_type': ['Da dầu/Hỗn hợp dầu'], 
        'skin_tone': None, 
        'size': None, 
        'sale': None, 
        'category': ['Chăm Sóc Da Mặt / Làm Sạch Da / Sữa Rửa Mặt', 'Chăm Sóc Da Mặt / Làm Sạch Da / Toner / Nước Cân Bằng Da'], 
        'brand': None, 
        'name': None, 
        'color_code': None
    }
}
