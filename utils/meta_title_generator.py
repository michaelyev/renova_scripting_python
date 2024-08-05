import openai
from dotenv import load_dotenv
load_dotenv()
import os
# Set your API key
openai.api_key = os.getenv("OPENAI_SECRET")

def meta_title_generator(text, model="gpt-3.5-turbo", max_tokens=150):
    prompt = f"Paraphrase the following text to avoid plagiarism 60-70 charactesr only:\n\n{text}"
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens
    )
    return response.choices[0]['message']['content'].strip()