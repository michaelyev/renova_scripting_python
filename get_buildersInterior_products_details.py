import os
import requests
from bs4 import BeautifulSoup
import json
from utils.meta_description_generator import meta_description_generator
from utils.meta_title_generator import meta_title_generator
from utils.filtering import extract_table_values

from utils.rewriter import rewriter


def download_image(image_url, product_model, category, output_dir='products'):
    try:
        response = requests.get(image_url)
        response.raise_for_status()

        # Create nested directories
        category_dir = os.path.join(output_dir, category)
        os.makedirs(category_dir, exist_ok=True)

        product_dir = os.path.join(category_dir, product_model)
        os.makedirs(product_dir, exist_ok=True)

        slides_dir = os.path.join(product_dir, 'slides')
        os.makedirs(slides_dir, exist_ok=True)

        # Extract image name from URL
        image_name = os.path.basename(image_url)
        image_path = os.path.join(slides_dir, image_name)

        with open(image_path, 'wb') as file:
            file.write(response.content)

        return image_path
    except Exception as e:
        return f"Error downloading image: {e}"
    
def extract_table_data(table):
    table_data = {}
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all(['th', 'td'])
        if len(cells) == 2:
            key = cells[0].get_text(strip=True)
            # Get the text within <p> tag if it exists
            value_tag = cells[1].find('p')
            if value_tag:
                value = value_tag.get_text(strip=True)
            else:
                value = cells[1].get_text(strip=True)
            table_data[key] = value
    return table_data
def get_color_group(table):
    return table.get("Color Group", None)

def scrape_product_data_and_download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the product model (title)
        product_model = soup.find('h1', class_='product_title entry-title').get_text(strip=True)
        
        # Extract the product description
        product_description = soup.find('div', class_='woocommerce-product-details__short-description').find('p').get_text(strip=True)

        # Extract the first table data
        table1 = soup.find('table')
        table_data1 = extract_table_data(table1)

        # Extract the second table data
        table2 = soup.find('table', class_='woocommerce-product-attributes shop_attributes')
        table_data2 = extract_table_data(table2)

        # Extract the image URL
        image_div = soup.find('div', class_='woocommerce-product-gallery__image')
        image_tag = image_div.find('img')
        image_url = image_tag['src']
        # If the image URL is relative, make it absolute
        if not image_url.startswith('http'):
            image_url = f"{url}/{image_url}"

        # Download the image
        image_path = download_image(image_url, product_model.replace(' ', '-').lower(), 'countertops')
        # Extract the brand specifically
        brand = table_data2.get('Brand', '')

        # Prepare the JSON-like dictionary
        sku_span = soup.find('span', class_='sku')
        pro_url = f'{product_model.replace(' ', '-').lower()}-{brand.replace(' ', '-').lower()}-{sku_span.text.strip().lower()}-{table_data2.get("Color Group", '').replace("/", "-").replace(" ", "").lower()}-{table_data2.get('Finish','').lower()}'
        meta_desc = meta_description_generator({
                "t1": table_data1,
                "t2": table_data2
            })
        meta_title = meta_title_generator(table1)
        color = get_color_group(table_data2)
        product_data = {
            'meta_description': meta_desc,
            'meta_title': meta_title,
            'url':pro_url,
            'brand': brand,
            'filtering':f'{meta_title} {extract_table_values([
                {"heading":"Details", "table":table_data1},
                {"heading":"Additional information", "table":table_data2},
            ])} {color} {brand}',
            'uid': product_model.replace(' ', '-').lower(),
            'model': product_model,
            'category': 'countertops',
            'specifications': [
                {"heading":"Details", "table":table_data1},
                {"heading":"Additional information", "table":table_data2},
            ],
            'images': [image_path],  # Store image path in a list
            'main_image':image_path,
            'color':color,
            'variants':[],
            'details': rewriter(product_description)
        }
        return product_data
    except Exception as e:
        return {'url': url, 'error': str(e)}

def get_buildersInteriors_products_data(urls):
    results = [scrape_product_data_and_download_image(url) for url in urls]
    return results

# if __name__ == '__main__':
#     urls = [
#         "https://www.buildersinteriors.com/shop/slab/msi/toasted-almond/",
#         "https://www.buildersinteriors.com/shop/slab/msi/tundra-gray-marble/"
#         # Add more URLs here
#     ]

#     # Run the main function and save the results
#     results = get_buildersInteriors_products_data(urls)

#     # Save results to a JSON file
#     with open('scraped_data.json', 'w', encoding='utf-8') as f:
#         json.dump(results, f, ensure_ascii=False, indent=4)

#     print("Scraping completed and data saved to scraped_data.json")
