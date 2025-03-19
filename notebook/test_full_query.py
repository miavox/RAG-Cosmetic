from src.utils import (
    generate_query_texts_fields,
    generate_query_texts_fields_with_brand_check,
    adjust_and_ensure_json,
    change_to_json
)
from src.database.search import ProductSearch
from src.function_calling.openAI_calling import CosmeticRequestAnalyzer
from src.llms.openAI import ChatOpenAI
from src.llms.gemini import GeminiRequestAnalyzer

# Khởi tạo các đối tượng cần thiết
llm = ChatOpenAI()
gemini = GeminiRequestAnalyzer()
analyzer = CosmeticRequestAnalyzer()
product_search = ProductSearch(verbose=True)

def test_cosmetic_recommendations(user_input: str):
    try:
        # Phân tích yêu cầu từ người dùng
        result = gemini.analyze_request_cosmetic(user_input)
        print("Analysis Result:", result)
        
        # Chuyển đổi kết quả sang JSON
        to_json = change_to_json(result)
        print("Converted to JSON:", to_json)
        
        to_json = adjust_and_ensure_json(to_json)
        print("Adjusted JSON:", to_json)
        
        # Tạo truy vấn tìm kiếm
        if to_json['comparison'] and len(to_json['special_requirements']['brand']) > 1:
            query_texts_fields = generate_query_texts_fields_with_brand_check(to_json)
        else:
            query_texts_fields = generate_query_texts_fields(to_json)
        print("Generated Query:", query_texts_fields)
        
        # Tìm kiếm sản phẩm
        results = product_search.search_combo_products_with_rewriting_gemini(
            query_texts_fields, to_json, gemini, user_input
        )
        
        print("Search Results:", results)
        return {"message": "Success", "data": results}
    except Exception as e:
        print("Error:", str(e))
        return {"message": "Error", "detail": str(e)}

# Chạy thử nghiệm
if __name__ == "__main__":
    user_test_input = "Tôi cần một bộ mỹ phẩm cho da dầu và có thể chống nắng."
    response = test_cosmetic_recommendations(user_test_input)
    print(response)