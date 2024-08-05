import aiohttp
import asyncio
import os
import json
from bs4 import BeautifulSoup
import re
from aiohttp import TCPConnector
from utils.meta_description_generator import meta_description_generator
from utils.meta_title_generator import meta_title_generator
from utils.price_decreaser import price_decreaser
from utils.rewriter import rewriter
from utils.filtering import extract_table_values

async def fetch(session, url):
    async with session.get(url, ssl=False) as response:
        if response.status == 200:
            return await response.text()
        else:
            raise Exception(f"Failed to fetch page content: {response.status}")
spec_data = []
def extract_specifications(soup):
    product_specifications = soup.find('div', class_='product-specifications')
    if not product_specifications:
        raise Exception("Product specifications div not found")
    for section in product_specifications.find_all('div', class_='spec-section'):
        header = section.find('p', class_='spec-head').get_text(strip=True)
        spec_dict = {}
        for item in section.find_all('li'):
            key = item.find('div', class_='spec-name').contents[0].strip()
            value_div = item.find('div', class_='spec-details')
            value = ', '.join([span.get_text(strip=True) for span in value_div.find_all('span')])
            spec_dict[key] = value

        spec_data.append({"heading": header, "table": spec_dict})

    return spec_data

def extract_name(soup):
    product_name = soup.find('span', class_='product-name')
    return product_name.get_text(strip=True) if product_name else None

def extract_price(soup):
    price_element = soup.find('div', class_='price')
    if not price_element:
        price_element = soup.find('div', class_='price price-sale')
    
    if price_element:
        # Extract the first numeric price value
        price_text = price_element.get_text(strip=True)
        price_match = re.search(r'\$\d+\.\d+', price_text)
        if price_match:
            return price_match.group().replace('$', '')
    return None

def extract_brand(soup):
    brand_element = soup.find('span', class_='product-brand')
    return brand_element.get_text(strip=True) if brand_element else None

def extract_model(soup):
    model_element = soup.find('span', class_='product-id')
    return model_element.get_text(strip=True) if model_element else None
# Dictionary to store the content
content_dict = {}

# Function to store the content with unique keys
def add_to_dict(tag_name, index, text, content_dict):
    key = f"{tag_name}{index}"
    content_dict[key] = text

# Initialize a counter dictionary
counters = {}

def scrape_content(element, counters, content_dict):
    for child in element.children:
        if child.name is not None:
            tag_name = child.name
            if tag_name not in counters:
                counters[tag_name] = 1
            index = counters[tag_name]
            text = child.get_text(strip=True)
            if text:
                # Check if the content is already in the dictionary
                if text not in content_dict.values():
                    if tag_name == 'ul':
                        ul_key = f"ul{index}"
                        content_dict[ul_key] = []
                        for li in child.find_all('li'):
                            content_dict[ul_key].append(li.get_text(strip=True))
                        counters['ul'] += 1
                    else:
                        if tag_name != 'li':
                            add_to_dict(tag_name, index, text, content_dict)
                            counters[tag_name] += 1
            # Recursive call to scrape nested content
            scrape_content(child, counters, content_dict)

def extract_product_details(soup):
    product_details = soup.find('div', class_='description-and-detail')
    return str(product_details)
async def download_images(session, soup, model):
    zoom_slider = soup.find('div', class_='product-image-zoom-slider')
    image_data = []

    if zoom_slider:
        product_images = zoom_slider.find_all('div', class_='product-image')
        model_folder = os.path.join('products', 'laminates', model)
        slides_folder = os.path.join(model_folder, 'slides')
        os.makedirs(slides_folder, exist_ok=True)

        for index, product_image in enumerate(product_images):
            img_tag = product_image.find('img')
            if img_tag and 'data-imgurl' in img_tag.attrs:
                img_url = img_tag['data-imgurl']

                async with session.get(img_url, ssl=False) as img_response:
                    if img_response.status == 200:
                        img_name = f"{model}_image_{index}.jpg"
                        img_path = os.path.join(slides_folder, img_name)

                        with open(img_path, 'wb') as f:
                            f.write(await img_response.read())

                        image_data.append(img_path.replace("\\", "/"))  # Ensure consistent path format
                    else:
                        print(f"Failed to download image {img_url}")
    return image_data
def get_text_after_p(url):
    try:
        text_after_p = url.split('/p/')[1]
        return text_after_p.replace('.html', '')
    except IndexError:
        return None
async def process_url(session, url):
    html_content = await fetch(session, url)
    soup = BeautifulSoup(html_content, 'html.parser')

    name = extract_name(soup)
    price = extract_price(soup)
    brand = extract_brand(soup)
    model = extract_model(soup)
    specifications = extract_specifications(soup)
    details = extract_product_details(soup)
    images = await download_images(session, soup, model)
    color = specifications[0].get('table').get('Color').lower()
    meta_title = meta_title_generator(name) 
    data = {
        'meta_description':meta_description_generator(specifications),
        'meta_title':meta_title,
        "url":  f'{get_text_after_p(url)}-{specifications[0].get('table').get('Color').lower()}',
        "uid":model,
        'filtering':f'{meta_title} {extract_table_values(specifications)} {color} {brand}',
        "price": price_decreaser(f'${price}'),
        "brand": brand,
        "model": model,
        "color":color,
        "category":"laminates",
        "specifications": specifications,
        "details":details,
        'variants': [],
        "main_image":images[1],
        "images": images,
    }
    return data

async def get_llflooring_products_data(urls):
    connector = TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [process_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

# if __name__ == '__main__':
#     urls = [
#         "https://www.llflooring.com/p/dream-home-xd-10mm-and-pad-delaware-bay-driftwood-laminate-flooring-7.6-in.-wide-x-54.45-in.-long-10050045.html",
#         "https://www.llflooring.com/p/dream-home-8mm-mountain-trail-oak-wpad-waterproof-laminate-flooring-8.03-in.-wide-x-48-in.-long-10054225.html"
#         # Add more URLs here
#     ]

#     # Run the main function and save the results
#     asyncio.run(get_llflooring_products_data(urls))
