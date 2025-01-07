from openai import OpenAI
import os
from src.prompts.prompt_calling import function_calling
import json
from dotenv import load_dotenv
import re

load_dotenv()

class CosmeticRequestAnalyzer:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)  
        self.prompt_cosmetic = function_calling

    def analyze_request(self, user_input):
        # Create a full prompt
        prompt = self.prompt_cosmetic + f' Đây là yêu cầu người dùng gửi vào: "{user_input}"'

        try:
            # Use the client to create a chat completion
            chat_completion = self.client.chat.completions.create(
                model="gpt-4o",  # Use "gpt-4" if accessible, or "gpt-3.5-turbo"
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Bạn là trợ lý tư vấn mua sắm chuyên về mỹ phẩm. Nhiệm vụ của bạn là tiếp nhận yêu cầu của khách hàng và phân tích yêu cầu để đưa ra các gợi ý sản phẩm phù hợp từ cơ sở dữ liệu."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4
            )

            # Process response from API
            if chat_completion and chat_completion.choices:
                reply = chat_completion.choices[0].message.content.strip()
                return reply
            else:
                raise ValueError("Không nhận được phản hồi hợp lệ từ API OpenAI.")

        except Exception as e:
            print("Error:", str(e))
            return f"Có lỗi xảy ra khi kết nối với OpenAI API: {str(e)}"

    def change_to_json(self, result):
        def sanitize_input(raw_input):
            """
            Sanitize raw input by removing formatting artifacts like backticks and fixing common issues.
            """
            sanitized_input = re.sub(r"^```(?:json)?|```$", "", raw_input.strip(), flags=re.MULTILINE)
            return sanitized_input.strip()

        def replace_nulls(obj):
            """
            Recursively replace all occurrences of the string "null" or None-like strings with None.
            """
            if isinstance(obj, dict):
                return {k: replace_nulls(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_nulls(item) for item in obj]
            elif obj in ["null", None]:  # Replace "null" string or actual None with Python None
                return None
            return obj

        try:
            sanitized_result = sanitize_input(result)
            parsed_json = json.loads(sanitized_result)
            return replace_nulls(parsed_json)

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return {"error": "Invalid JSON format", "special_requirements": {}}