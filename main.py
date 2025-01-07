from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.utils import generate_query_texts_fields, generate_query_texts_fields_with_brand_check, adjust_and_ensure_json
from src.database.search import ProductSearch
from src.function_calling.openAI_calling import CosmeticRequestAnalyzer
from src.llms.openAI import ChatOpenAI

# Khởi tạo FastAPI
app = FastAPI()
llm = ChatOpenAI()

# Khởi tạo các đối tượng cần thiết
analyzer = CosmeticRequestAnalyzer()
product_search = ProductSearch(verbose=True)

# Định nghĩa dữ liệu đầu vào
class UserInput(BaseModel):
    user_input: str

# API endpoint
@app.post("/cosmetic-recommendation-text/")
async def cosmetic_recommendations(input_data: UserInput):
    try:
        # Phân tích yêu cầu từ người dùng
        result = analyzer.analyze_request(input_data.user_input)
        print(result)
        
        # Chuyển đổi kết quả sang JSON
        to_json = analyzer.change_to_json(result)
        print(to_json)
        
        to_json = adjust_and_ensure_json(to_json)
        print(to_json)
        
        if to_json['comparison'] and len(to_json['special_requirements']['brand']) > 1:
            query_texts_fields = generate_query_texts_fields_with_brand_check(to_json)
            print(query_texts_fields)
        else:
            query_texts_fields = generate_query_texts_fields(to_json)
            print(query_texts_fields)
        
        # Tìm kiếm sản phẩm và trả về kết quả
        results = product_search.search_combo_products_with_rewriting(query_texts_fields, to_json, llm, input_data.user_input)
        
        # Trả dữ liệu về cho người dùng
        return {"message": "Success", "data": results}
    except Exception as e:
        # Trường hợp xảy ra lỗi
        raise HTTPException(status_code=500, detail=str(e))
