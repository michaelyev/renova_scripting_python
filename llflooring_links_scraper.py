import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from urllib.parse import urljoin

async def fetch(url, session):
    try:
        async with session.get(url, ssl=False) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

async def extract_links(base_url, url, session):
    html_content = await fetch(url, session)
    if html_content is None:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    links = []
    for a_tag in soup.find_all('a', class_='pdp-link'):
        href = a_tag['href']
        full_url = urljoin(base_url, href)  # Create full URL
        links.append(full_url)
    return links

async def scrape_all_pages(base_url, min, max):
    async with ClientSession() as session:
        tasks = []
        for page in range(min, max + 1):
            sz_value = page * 24  # Calculate the `sz` value based on the page number
            url = f"{base_url}?sz={sz_value}"
            tasks.append(extract_links(base_url, url, session))
        
        results = await asyncio.gather(*tasks)
        all_links = [link for sublist in results for link in sublist]
        return all_links

# Run the event loop to scrape all pages
def scrape_product_links_llflooring(base_url, min, max):
    return scrape_all_pages(base_url, min, max)

# # Example usage
# if __name__ == "__main__":
#     base_url = "https://www.llflooring.com/c/laminate-flooring/"
#     max = 1  # Set this to the number of pages you want to scrape
#     links = scrape_product_links_llflooring(base_url, max)
#     print(links)
