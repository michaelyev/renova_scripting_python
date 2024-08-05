import openai
from dotenv import load_dotenv
load_dotenv()
import os
openai.api_key = os.getenv("OPENAI_SECRET")

def filtering_string_generator(description, model="gpt-3.5-turbo", max_tokens=150):
    prompt = (
        f"Please convert the following key-value pairs into a single string containing only the values, separated by spaces. "
        f"Example: if you get key:value, key:value then make simple string value value: '{description}'"
    )
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens
    )
    return response.choices[0].message['content'].strip()
