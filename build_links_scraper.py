import asyncio
import aiohttp
import ssl
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Disable SSL certificate verification
ssl_context = ssl.SSLContext()
ssl_context.verify_mode = ssl.CERT_NONE

async def fetch(url, session):
    async with session.get(url, ssl=ssl_context) as response:
        return await response.text()

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(fetch(url, session))
        return await asyncio.gather(*tasks)

def extract_hrefs(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', {'data-automation': 'product-card-description-link'})
    return [link.get('href') for link in links]

async def scrape_product_links_build(base_url, start_page, end_page):
    urls = [f"{base_url}&page={i}" for i in range(start_page, end_page)]
    html_pages = await fetch_all(urls)
    all_hrefs = []
    for html in html_pages:
        all_hrefs.extend(extract_hrefs(html))
    # Prepend base_url to relative links
    complete_links = [urljoin(base_url, href) for href in all_hrefs]
    return complete_links

# # Example usage
# base_url = 'https://www.build.com/shop-all-vanities/c113572?page='
# start_page = 1
# end_page = 3  # Set the end page number

# product_links = scrape_product_links_build(base_url, start_page, end_page)

# # Save as JSON file
# output_filename = "build-products-links.json"
# with open(output_filename, "w") as json_file:
#     json.dump(product_links, json_file)

# print("Total URLs extracted:", len(product_links))
# print("Data saved to", output_filename)
