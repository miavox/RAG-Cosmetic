from src.function_calling.openAI_calling import CosmeticRequestAnalyzer
from src.llms.gemini import GeminiRequestAnalyzer
import time
from src.utils import change_to_json
start_time = time.time()

# analyzer = CosmeticRequestAnalyzer()
gemini = GeminiRequestAnalyzer()

user_input = "so sánh kem nền maybelline kiềm dầu và l'oreal"
result = gemini.analyze_request_cosmetic(user_input)
end_time = time.time()


# Calculate time taken
time_taken = end_time - start_time

print(f"Time taken for request: {time_taken:.2f} seconds")
print(result)

to_json = change_to_json(result)
print(to_json)