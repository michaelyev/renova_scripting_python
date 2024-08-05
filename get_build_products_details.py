import requests
from bs4 import BeautifulSoup
import json
import os
import threading
from typing import List
from fastapi import FastAPI
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
import time
from utils.meta_description_generator import meta_description_generator
from utils.getBuildProductColor import get_color_for_url
from utils.filtering import extract_table_values
from utils.meta_title_generator import meta_title_generator
from utils.price_decreaser import price_decreaser
from utils.ImageNavigationMaker import extract_filename_from_url
import urllib.parse
lock = threading.Lock()

load_dotenv()

app = FastAPI()



def download_main_image(image_url, save_directory):
    try:
        parsed_url = urllib.parse.urlparse(image_url)
        image_name = os.path.basename(parsed_url.path)
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(image_url, headers=headers, stream=True)
        if response.status_code == 200:
            image_path = os.path.join(save_directory, 'main.jpg')
            with open(image_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            return image_path
        else:
            print(f"Failed to retrieve the image. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

def fetch_main_image(soup, category_name, model):
    try:
        # Find the image tag by class name
        img_tag = soup.find('div', class_='transform-component-module_content__FBWxo').find('img')
        if img_tag:
            # Get the image source URL
            image_url = img_tag.get('src')
            # Extract filename from URL
            parsed_url = urllib.parse.urlparse(image_url)
            filename = os.path.basename(parsed_url.path)
            # Construct the full path
            folder_path = os.path.join('products', category_name, model, 'slides')
            image_path = os.path.join(folder_path, 'main.jpg')
            # Download the image
            if not os.path.exists(image_path):
                download_path = download_main_image(image_url, folder_path)
                if download_path:
                    print(f"Image downloaded successfully: {download_path}")
                else:
                    print("Image download failed.")
                    return None
            
            # Return the full path
            return [image_path, image_url]
        else:
            print("Image tag not found.")
            return None
    except Exception as e:
        print(f"Error fetching main image: {e}")
        return None

def find_colors_and_models_with_part(models, target):
    target_suffix = '-'.join(target.split('-')[1:])  # Extract the suffix part (2209-0)
    match = next((item for item in models if '-'.join(item['model'].split('-')[1:]) == target_suffix), None)
    return match

def download_image(url, folder_path, image_name):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        with open(os.path.join(folder_path, image_name), 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {image_name} in {folder_path}")
    except Exception as e:
        print(f"Error downloading {image_name}: {e}")

def process_url(url, base_image_folder, products_json):
    variant_images_data = []
    slide_images_data = []
    try:
        # Scrape the data using BeautifulSoup
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the span tags with the specific attributes and class names
        price_span = soup.find('span', {'data-automation': 'price'})
        model_span = soup.find('span', {'data-automation': 'product-model-number', 'class': 'b'})
        product_title_span = soup.find('span', {'class': 'fw2 di-ns'})
        h1_tag = soup.find('h1', class_='lh-title')
        parsed_url = urlparse(url)
        uid = parse_qs(parsed_url.query).get('uid', [None])[0]
        if price_span:
            price = price_span.text.strip()
        else:
            price = "Price not found"

        # Find the span element with the specified data-automation attribute
        model_number_span = soup.find('span', {'data-automation': 'product-model-number'})

        # Extract the text content
        if model_number_span:
            model = model_number_span.get_text().replace(" ","")
        else:
            print("Product model number not found.")

        if product_title_span:
            product_title = product_title_span.text.strip()
        else:
            product_title = "Product title not found"
        
        # Find the <div> element with class 'lh-copy H_oFW'
        div_element = soup.find('div', class_='lh-copy H_oFW')
        # Get the HTML content of the <div> element
        if div_element:
            # details_content = get_details_part(div_element)  # Get the prettified HTML content
            details_content = str(div_element)  # Get the prettified HTML content

        else:
            print("No <div> element found with class 'lh-copy H_oFW'")
        if h1_tag:
            first_span = h1_tag.find('span')
            if first_span:
                brand = first_span.text.strip()
                print(f"Brand: {brand}")
            else:
                print("No <span> tag found inside the <h1> tag")
        else:
            print("No <h1> tag with class 'lh-title' found")


        # Find all the table containers
        table_divs = soup.find_all('div', class_='w-100 w-third-ns')
        all_tables_data = []
        for table_div in table_divs:
            # Find the heading text dynamically
            nested_divs = table_div.find_all('div', class_='db-ns')

            for nested_div in nested_divs:
                heading_tag = nested_div.find('h3', class_='f4 ma0 mt4')
                heading = heading_tag.get_text(strip=True) if heading_tag else 'No Heading'
                tbodies = nested_div.find_all('tbody')

                for tbody in tbodies:
                    tbody_data = {}
                    rows = tbody.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) == 2:
                            key = cols[0].get_text(strip=True)
                            value = cols[1].get_text(strip=True)
                            tbody_data[key] = value
                    if tbody_data:
                        table_data = {'heading': heading, 'table': tbody_data}
                        all_tables_data.append(table_data)
        meta_description = meta_description_generator(all_tables_data)
        meta_title = meta_title_generator(product_title)
        newprice = price_decreaser(price)
        # Create directories for the product
        root_folder = 'products'
        main_folder = os.path.join(root_folder, base_image_folder)
        product_folder = os.path.join(main_folder, model)
        os.makedirs(product_folder, exist_ok=True)
        # Create subfolders for slide and variant images
        slide_folder = os.path.join(product_folder, 'slides')
        os.makedirs(slide_folder, exist_ok=True)
        model_color = []
        main_image = fetch_main_image(soup, base_image_folder, model)
        if main_image:
            print(main_image)
        def download_images_from_divs(div_class, type):
            image_divs = soup.find_all('div', class_=div_class)
            folder = slide_folder
     
            for index, div in enumerate(image_divs):
                img_tag = div.find('img')
                if img_tag and 'src' in img_tag.attrs:
                    img_url = img_tag['src']
                    img_name = f'{type}_image_{index+1}.jpg'
                    if type == 'variant':
                        color_div = div.find('div', style=True)
                        if color_div:
                            style = color_div.get('style')
                            color = style.split('background-color:')[1].split(';')[0].strip()
                            img_name = f'{type}_image_{index+1}.jpg'
                            variant_images_data.append({'color_name': color, 'model':extract_filename_from_url(img_url)})
                    
                    if type == 'slide':
                        download_image(img_url, folder, img_name)
                        slide_images_data.append(f'products/{base_image_folder}/{model}/slides/{img_name}')

        # Download images
        download_images_from_divs('br2', 'variant')
        download_images_from_divs('transform-component-module_content__FBWxo', 'slide')

        # Generate rewrite for details content
        # details_content = generate_rewrite(details_content)

        # Save the extracted table data and other details to a JSON file
        # Find the <span> with data-automation="finish-name"
        pro_url = f'{brand.replace(" ", "-").lower()}-{model}-{uid}'
        pcolor = get_color_for_url(url)
        product_data = {
            'meta_description':meta_description,
            'meta_title':meta_title,
            'url':pro_url,
            'brand':brand,
            'uid':uid,
            'filtering':f'{meta_title} {extract_table_values(all_tables_data)} {pcolor} {brand}',
            'image_navigation':'' if len(variant_images_data) == 0 else extract_filename_from_url(main_image[1]),
            'price': newprice,
            'model': '' if len(variant_images_data) == 0 else extract_filename_from_url(main_image[1]),
            # 'color':find_colors_and_models_with_part(variant_images_data, model)[0][0],
            'color':pcolor,
            'category':base_image_folder.lower(),
            'specifications': all_tables_data,
            'variants': variant_images_data,
            'images': slide_images_data,
            'main_image':main_image[0],
            "details": details_content
        }
        # # Save product data to a JSON file
        # product_folder = os.path.join(base_image_folder, model.lower())
        # os.makedirs(product_folder, exist_ok=True)
        # product_json_path = os.path.join(product_folder, f"{model}.json")
        # with open(product_json_path, 'w', encoding='utf-8') as json_file:
        #     json.dump(product_data, json_file, ensure_ascii=False, indent=4)

        # Append product data to the shared list
        with lock:
            products_json.append(product_data)
    except Exception as e:
        print(f"Error processing URL {url}: {e}")
def get_build_products_data(urls, base_image_folder):
    products_json = []

    threads = []

    for index, url in enumerate(urls):
        try:
            thread = threading.Thread(target=process_url, args=(url, base_image_folder, products_json))
            threads.append(thread)
            thread.start()

            if index < len(urls) - 1:  # Check if this is not the last URL
                time.sleep(1)  # Sleep for 1 second before starting the next thread

        except Exception as e:
            print(f"Error creating thread for URL {url}: {e}")

    for thread in threads:
        thread.join()
    return products_json
# class URLRequest(BaseModel):
#     urls: List[str]
#     folder: str

# @app.post("/save_build_products")
# async def get_products_details(request: URLRequest):
#     products = get_build_products_data(request.urls, request.folder)
#     return products
# get_build_products_data(["https://www.build.com/fresca-fcb8360-d-i/s1464639?uid=3445794&searchId=IYnbooAhB6"], "tile")