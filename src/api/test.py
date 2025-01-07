from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.utils import generate_query_texts_fields
from src.database.search import ProductSearch
from src.function_calling.openAI_calling import CosmeticRequestAnalyzer

# Khởi tạo FastAPI
app = FastAPI()

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
        
        # Chuyển đổi kết quả sang JSON
        to_json = analyzer.change_to_json(result)
        
        # Tạo query_texts_fields từ JSON
        query_texts_fields = generate_query_texts_fields(to_json)
        
        # Tìm kiếm sản phẩm và trả về kết quả
        results = product_search.transform_to_target_structure_fixed(query_texts_fields, to_json)
        
        # Trả dữ liệu về cho người dùng
        return {"message": "Success", "data": results}
    except Exception as e:
        # Trường hợp xảy ra lỗi
        raise HTTPException(status_code=500, detail=str(e))
