from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

class ChatOpenAI:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key = self.api_key)

    def analyze_request(self, user_input, prompt_function, model = "gpt-3.5-turbo", system_message = None, temperature = 0.4):
        try:
            # Generate the prompt using the provided function
            prompt = prompt_function(user_input)

            # Construct the messages payload for the API
            messages = []
            if system_message:
                messages.append({
                    "role": "system",
                    "content": system_message
                })
            messages.append({
                "role": "user",
                "content": prompt
            })

            # Use the OpenAI client to get a chat completion
            chat_completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature
            )

            # Process and return the API response
            if chat_completion and chat_completion.choices:
                reply = chat_completion.choices[0].message.content.strip()
                return reply
            else:
                raise ValueError("Cannot get a valid response from the OpenAI API.")

        except Exception as e:
            print("Error:", str(e))
            return f"Error connecting to OpenAI API: {str(e)}"