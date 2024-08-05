import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup

async def fetch(url, session):
    try:
        async with session.get(url, ssl=False) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

async def extract_links(url, session):
    html_content = await fetch(url, session)
    if html_content is None:
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    links = []
    for a_tag in soup.find_all('a', class_='woocommerce-LoopProduct-link woocommerce-loop-product__link'):
        href = a_tag['href']
        links.append(href)
    return links

async def scrape_all_pages(base_url, min,max):
    async with ClientSession() as session:
        tasks = []
        for page in range(min, max + 1):
            url = f"{base_url}&paged={page}"
            tasks.append(extract_links(url, session))
        
        results = await asyncio.gather(*tasks)
        all_links = [link for sublist in results for link in sublist]
        return all_links


# Run the event loop to scrape all pages
def scrape_product_links_buiders_interiors(base_url,min, max):
    # base_url = "https://www.buildersinteriors.com/shop/slab/?bi=1&really_curr_tax=49-product_cat"
    # max = 3  # Set this to the number of pages you want to scrape
    return scrape_all_pages(base_url, min,max)
