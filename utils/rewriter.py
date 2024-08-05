import openai
from dotenv import load_dotenv
load_dotenv()
import os
openai.api_key = os.getenv("OPENAI_SECRET")

def rewriter(description, model="gpt-3.5-turbo", max_tokens=1500):
    prompt = f"Rewrite the content of each HTML tag while ensuring the meaning remains consistent. Focus on varying sentence structure, synonyms, and phrasing to create distinct but semantically equivalent content'{description}'"
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens
    )
    return response.choices[0]['message']['content'].strip()