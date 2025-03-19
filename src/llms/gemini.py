import requests
import json
import os
from dotenv import load_dotenv
from src.prompts.prompt_calling import function_calling

load_dotenv()

class GeminiRequestAnalyzer:
    def __init__(self, api_keys=None):
        self.api_keys = os.getenv("GEMINI_API_KEY").split(',') if api_keys is None else api_keys
        self.prompt_gemini = function_calling
    
    def analyze_request_cosmetic(self, text):
        api_url_template = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-002:generateContent?key={}"
        prompt = self.prompt_gemini + f" Đây là yêu cầu người dùng gửi vào: \"{text}\""
        
        request_body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 800,
                "temperature": 0.4,
                "topP": 0.95
            }
        }
        
        headers = {"Content-Type": "application/json"}
        
        for api_key in self.api_keys:
            api_url = api_url_template.format(api_key.strip())
            try:
                response = requests.post(api_url, headers=headers, json=request_body)
                if response.status_code == 429:
                    print("Rate limit exceeded. Switching API key...")
                    continue  # Chuyển sang API key tiếp theo
                response.raise_for_status()
                result = response.json()

                print("Raw API response:", json.dumps(result, indent=2))

                if result and "candidates" in result and len(result["candidates"]) > 0:
                    response_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                    print("Processed response text:", response_text)
                    return response_text
                else:
                    print("Unexpected API response:", result)
                    return {"message": "error", "answer": "An error occurred while processing your request."}
            except requests.exceptions.RequestException as error:
                print("API request failed:", error)
        
        return {"message": "error", "answer": "All API keys exhausted."}
    
    def analyze_request(self, prompt):
        api_url_template = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-002:generateContent?key={}"
        
        request_body = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 800,
                "temperature": 0.4,
                "topP": 0.95
            }
        }
        
        headers = {"Content-Type": "application/json"}
        
        for api_key in self.api_keys:
            api_url = api_url_template.format(api_key.strip())
            try:
                response = requests.post(api_url, headers=headers, json=request_body)
                if response.status_code == 429:
                    print("Rate limit exceeded. Switching API key...")
                    continue  # Chuyển sang API key tiếp theo
                response.raise_for_status()
                result = response.json()

                print("Raw API response:", json.dumps(result, indent=2))

                if result and "candidates" in result and len(result["candidates"]) > 0:
                    response_text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                    print("Processed response text:", response_text)
                    return response_text
                else:
                    print("Unexpected API response:", result)
                    return {"message": "error", "answer": "An error occurred while processing your request."}
            except requests.exceptions.RequestException as error:
                print("API request failed:", error)
        
        return {"message": "error", "answer": "All API keys exhausted."}
