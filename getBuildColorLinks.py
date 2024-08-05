import asyncio
import aiohttp
import ssl
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

# Disable SSL certificate verification
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async def fetch(url, session):
    async with session.get(url, ssl=ssl_context) as response:
        return await response.text()

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(url, session) for url in urls]
        return await asyncio.gather(*tasks)

def extract_hrefs(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', {'data-automation': 'product-card-description-link'})
    return [link.get('href') for link in links]

async def scrape_product_links_build(base_url, start_page, end_page):
    # Modify URL construction to change page number
    urls = [f"{base_url}&page={i}" for i in range(start_page, end_page + 1)]
    html_pages = await fetch_all(urls)
    all_hrefs = []
    for html in html_pages:
        all_hrefs.extend(extract_hrefs(html))
    # Prepend base_url to relative links
    complete_links = [urljoin(base_url, href) for href in all_hrefs if href]
    return complete_links

# Example usage
start_page = 1
end_page = 208  # Set the end page number
base_url = 'https://www.build.com/kohler-kitchen-sinks/c109356?facets=masterFinishes_ss:Blacks'  # Base URL without page number

# Running the async function and getting results
product_links = asyncio.run(scrape_product_links_build(base_url, start_page, end_page))

# Save as JSON file
output_filename = "sink-blacks-links.json"
with open(output_filename, "w") as json_file:
    json.dump(product_links, json_file)

print("Total URLs extracted:", len(product_links))
print("Data saved to", output_filename)
