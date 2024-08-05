import openai
from dotenv import load_dotenv
load_dotenv()
import os

# def meta_description_generator(description):
#     try:
#         client = openai.Client(api_key=os.getenv("OPENAI_SECRET"))
#         completion = client.completions.create(
#             model="gpt-3.5-turbo-instruct",
#             prompt=f"based on provided tables data ready comprehensive meta description that highlights key features from each table with english words must cover within 100 characters only'{description}'",
#             max_tokens=150,
#             temperature=0
#         )
#         generated_text = completion.choices[0].text.strip()
#         # Remove any surrounding quotes if present
#         if generated_text.startswith('"') and generated_text.endswith('"'):
#             generated_text = generated_text[1:-1]
#         return generated_text
#     except Exception as e:
#         print(f"Error decreasing price: {e}")
#         return description
    


# Set your API key
openai.api_key = os.getenv("OPENAI_SECRET")

def meta_description_generator(description, model="gpt-3.5-turbo", max_tokens=1000):
    prompt = f"based on provided tables data ready comprehensive meta description that highlights key features from each table with english words must cover within 100 characters only'{description}'"
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens
    )
    return response.choices[0]['message']['content'].strip()
