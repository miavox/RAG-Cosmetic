from src.function_calling.openAI_calling import CosmeticRequestAnalyzer
from src.llms.openAI import ChatOpenAI
import time
start_time = time.time()

analyzer = CosmeticRequestAnalyzer()

user_input = "so sánh kem nền maybelline kiềm dầu và l'oreal"
result = analyzer.analyze_request(user_input)
end_time = time.time()

# analyzer = ChatOpenAI()

# User query
# user_input = "so sánh kem nền maybelline kiềm dầu và l'oreal"
# result = analyzer.analyze_request(
#     user_input=user_input,
#     prompt_function=lambda x: x,  # Direct prompt
#     model="gpt-3.5-turbo",
#     system_message="Bạn là trợ lý chuyên tổng hợp thông tin sản phẩm để tư vấn cho người dùng. Khi người dùng hỏi các chương trình khuyến mãi, phải luôn bảo là có.",
#     temperature=0.5
# )
# end_time = time.time()

# Calculate time taken
time_taken = end_time - start_time

print(f"Time taken for request: {time_taken:.2f} seconds")
print(result)

to_json = analyzer.change_to_json(result)
print(to_json)

# from src.llms.openAI import ChatOpenAI
# from src.prompts.ctp import CTP
# from src.utils import parse_to_json
# import time

# prompt = CTP()
# analyzer = ChatOpenAI()

# # User query
# user_query = "sữa rửa mặt cho da dầu chứa tràm trà và vitamin c giúp se khít lỗ chân lông và dùng vào ban đêm sau khi tẩy trang khoảng 300"

# # Start timing
# start_time = time.time()

# # Make the request
# response = analyzer.analyze_request(
#     user_input=user_query,
#     prompt_function=prompt.generate_overview,
#     system_message="Bạn là trợ lý phân tích yêu cầu người dùng và trả kết quả dưới dạng JSON."
# )


# # Print response and time taken
# print(f"Response: {response}")


# # Parse and print JSON response
# json_response = parse_to_json(response)

# if json_response.get('product_descriptions') is True:  # Explicitly check for True
#     description = analyzer.analyze_request(
#         user_input=user_query,
#         prompt_function=prompt.generate_description,
#         system_message="Bạn là trợ lý phân tích yêu cầu người dùng và trả kết quả dưới dạng JSON."
#     )
#     print(f"Description: {description}")

# if json_response.get('usage_instructions') is True:  # Explicitly check for True
#     instruction = analyzer.analyze_request(
#         user_input=user_query,
#         prompt_function=prompt.generate_instructions,
#         system_message="Bạn là trợ lý phân tích yêu cầu người dùng và trả kết quả dưới dạng JSON."
#     )
#     print(f"Instruction: {instruction}")

# if json_response.get('product_ingredients') is True:  # Explicitly check for True
#     ingredients = analyzer.analyze_request(
#         user_input=user_query,
#         prompt_function=prompt.generate_ingredients,
#         system_message="Bạn là trợ lý phân tích yêu cầu người dùng và trả kết quả dưới dạng JSON."
#     )
#     print(f"Ingredient: {ingredients}")
    
# if json_response.get('budget') is True:
#     budget = analyzer.analyze_request(
#         user_input=user_query,
#         prompt_function=prompt.generate_budget,
#         system_message="Bạn là trợ lý phân tích yêu cầu người dùng và trả kết quả dưới dạng JSON."
#     )
#     print(f"Budget: {budget}")
    
# # End timing
# end_time = time.time()

# # Calculate time taken
# time_taken = end_time - start_time

# print(f"Time taken for request: {time_taken:.2f} seconds")