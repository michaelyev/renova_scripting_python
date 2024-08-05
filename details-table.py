import requests
from bs4 import BeautifulSoup
import openai

# Function to rewrite text using OpenAI API
def rewrite_text(text, api_key):
    openai.api_key = api_key
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Rewrite the following description to make it more engaging and clear:\n\n{text}",
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()

# Your OpenAI API key
api_key = ''

# URL to scrape
url = "https://www.build.com/kohler-k-6489/s562806?uid=1740930&searchId=ZvXfD3GDiX"

# Scrape the data using BeautifulSoup
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extract the relevant data
lh_copy_div = soup.find('div', class_='lh-copy H_oFW')
paragraphs = lh_copy_div.find_all('p')
lists = lh_copy_div.find_all('ul')

original_text = ""

# Combine all text from paragraphs and lists
for p in paragraphs:
    original_text += p.get_text() + "\n\n"

for ul in lists:
    for li in ul.find_all('li'):
        original_text += "- " + li.get_text() + "\n"

# Rewrite the text using OpenAI
rewritten_text = rewrite_text(original_text, api_key)

# Print the rewritten text (or save it as needed)
print("Original Text:\n", original_text)
print("\nRewritten Text:\n", rewritten_text)

# Save the rewritten text to a file (optional)
with open('rewritten_description.txt', 'w') as file:
    file.write(rewritten_text)

