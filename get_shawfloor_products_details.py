import os
import requests
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import pandas as pd
from fastapi import FastAPI
from selenium.webdriver.chrome.options import Options
import openai
import threading
import queue
from utils.meta_description_generator import meta_description_generator
from utils.filtering import extract_table_values
from utils.meta_title_generator import meta_title_generator
from utils.price_decreaser import price_decreaser
from utils.rewriter import rewriter
from utils.getProductColor import get_color_for_url
from dotenv import load_dotenv
load_dotenv()
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

base_url = "http://localhost:8000/"

app = FastAPI()


def rewrite_description(description):
    try:
        client = openai(api_key=os.getenv("OPENAI_SECRET"))
        completion = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Please generate or rewrite given description for meta description within 60 to 150 characters using all parameters and please remove all dirty or useless data '{description}'",
            max_tokens=500,
            temperature=0
        )
        return completion.choices[0].text.strip()
    except Exception as e:
        print(f"Error generating rewrite: {e}")
        return description

def modify_image_url(image_url, width=500, height=500):
    parsed_url = urlparse(image_url)
    query_params = parse_qs(parsed_url.query)

    # Update width and height parameters
    query_params['w'] = [str(width)]
    query_params['h'] = [str(height)]

    # Reconstruct the URL with updated query parameters
    new_query = urlencode(query_params, doseq=True)
    modified_url = urlunparse(parsed_url._replace(query=new_query))
    return modified_url

def download_image(image_url, save_directory):
    try:
        modified_url = modify_image_url(image_url)
        parsed_url = urlparse(modified_url)
        image_name = os.path.basename(parsed_url.path)
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(modified_url, headers=headers, stream=True)
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

def extract_table_data(driver, accordion_header_ids):
    try:
        data = {}
        for header_id in accordion_header_ids:
            try:
                header = driver.find_element(By.ID, header_id)
                header.click()
                time.sleep(3)
            except:
                pass
            
        # Wait for the table to be visible
        table = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#full-product-details-specs .specs .table.table-striped'))
        )
        
        rows = table.find_elements(By.TAG_NAME, 'tr')
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) == 2:
                key = cells[0].text.strip()
                value = cells[1].text.strip()
                data[key] = value
        return data
    except Exception as e:
        print(f"Error extracting table data: {e}")
        return {}

def download_slider_image(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)
    print(f"Downloaded image {filename}")

def get_text_after_segment(url, segment):
    parts = url.split('/')
    try:
        return '/'.join(parts[parts.index(segment) + 1:])
    except ValueError:
        return None
    
def get_all_product_details(url, category):
    main_color = get_color_for_url(url)
    try:
        last_segment = get_text_after_segment(url, 'details')
        if last_segment:
            last_segment = last_segment.replace(" ", '-').lower()
        else:
            print("Error: Segment 'details' not found in URL.")
            return None
        
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))).click()
        except:
            pass
        product_details_container = driver.find_element(By.ID, 'full-product-details-header-desktop')
        about_section = driver.find_element(By.ID, 'full-product-details-about')
        details_content = about_section.text.strip().split("Learn more")[0].strip()
        accordion_header_ids = ['headingOne']
        table_data = extract_table_data(driver, accordion_header_ids)
        swatch_items = driver.find_elements(By.CLASS_NAME, 'swatch-item')
        details_content = rewrite_description(details_content)
        price = product_details_container.find_element(By.CLASS_NAME, 'price-amount').text.strip()
        price = price_decreaser(f'${price}')
 
        thumb_slider = driver.find_element(By.CSS_SELECTOR, 'div.thumb-slider')
        # Directory setup
        main_directory = "products"
        category_directory = os.path.join(main_directory, category)
        product_directory = os.path.join(category_directory, last_segment.replace("/", "-").replace(" ", "").lower())
        slide_directory = os.path.join(product_directory, "slides")
        os.makedirs(slide_directory, exist_ok=True)
        # Initialize a list to store the image data
        image_data = []
        slide_data = []
        main_image = ''
        parsed_url = urlparse(url)
        path_components = parsed_url.path.split('/')
        product_id = path_components[-2].replace('-', ' ')  # Replace hyphens with spaces
        product_name = path_components[-1].replace('-', ' ')  # Replace hyphens with spaces
        title = f'{product_name} {product_id}'
        # image_url = fetch_image_url(driver)
        # print(image_url, "gh8")
        for item in swatch_items:
            try:
                color_name = item.find_element(By.CLASS_NAME, 'item-color-name').get_attribute('innerHTML').replace('<br>', ' ')
                formatted_color_name = '-'.join(color_name.lower().split())
                background_image_style = item.find_element(By.CLASS_NAME, 'swatchThumb').get_attribute('style')
                background_image_url = background_image_style.split('url(')[-1].split(');')[0].strip('\'"')
                print(f'{product_name.replace(" ", "-").lower()}-{table_data.get("Color", "").split(" ")[0].lower()}', 'jani1')
                print(table_data.get("Color"), 'jan7')
                print(table_data)
                print(formatted_color_name, 'jani2')
                if formatted_color_name == f'{product_name.replace(" ", "-").lower()}-{table_data.get("Color", "").split(" ")[0].lower()}':
                    print(background_image_url)
                    image_path = download_image(background_image_url, slide_directory)
                    main_image = image_path
                image_data.append({"model": formatted_color_name})

            except Exception as e:
                print(f"Error processing swatch item: {e}")
        if thumb_slider:
            # Extract big images
            big_images = driver.find_elements(By.CSS_SELECTOR, '.thumb-slider .aSlide:not([tabindex="-1"])')
            for i, slide in enumerate(big_images):
                # Extract big image URL
                big_image_url = slide.get_attribute('data-url')
                big_image_path = os.path.join(slide_directory, f'slide_image_{i}.jpg')
                # Download image
                download_slider_image(big_image_url, big_image_path)
                print(os.path.relpath(big_image_path, start=main_directory), '90')
                # Add image URL and path to the image_data list
                slide_data.append(big_image_path)
            # Save the image data to a JSON file
            with open('slider-images.json', 'w') as json_file:
                json.dump(image_data, json_file, indent=4)
            print("Image data saved to slider-images.json")
        else:
            print("Thumbnail slider not found.")
        title = f'{product_name} {product_id}' 
        pro_url = f'{product_id.replace(" ", "-").lower()}-{product_name.replace(" ", "-").lower()}-{table_data.get("Width", "").replace(" ", "")}-{table_data.get("Collection", "").replace(" ", "-").lower()}' 
        meta_title = meta_title_generator(title)
        product_details = {
            'meta_description': meta_description_generator({"t1": table_data}),
            'meta_title': meta_title,
            'url': pro_url,
            'uid': product_id.replace(" ", "-").lower(),
            'filtering':f'{meta_title} {extract_table_values([{"heading":"Details", "table":table_data}])} {main_color}',
            'image_navigation': f'{product_name.replace(" ", "-").lower()}-{table_data.get("Color", "").split(" ")[0].lower()}',
            'price': price,
            'color':main_color,
            'brand': 'shawfloors',
            'model': product_id.replace(" ", "-").lower(),
            'category': category.lower(),
            'specifications': [{"heading":"Details", "table":table_data}],
            'variants': image_data,
            'images': slide_data,
            'main_image': main_image,
            "details": details_content
        }
        with open("product-details.json", "a") as json_file:
            json.dump(product_details, json_file, indent=4)
        
        return product_details
    except Exception as e:
        print(f"Error scraping product details: {e}")
        return None
    finally:
        driver.quit()

def process_url(url, results_queue, category):
    try:
        product_details = get_all_product_details(url, category)
        if product_details:
            print(f"Product details scraped successfully for URL: {url}")
            results_queue.put(product_details)
        else:
            print(f"Failed to scrape product details for URL: {url}")
    except Exception as e:
        print(f"Error processing URL {url}: {e}")

def get_shawfloor_products_data(urls, category):
    threads = []
    results_queue = queue.Queue()

    for url in urls:
        thread = threading.Thread(target=process_url, args=(url, results_queue, category))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    results = []
    while not results_queue.empty():
        results.append(results_queue.get())
    return results

# Example usage:
# urls = [
#     "https://shawfloors.com/flooring/carpet/details/vintage-revival-cc77b/turmeric",
#     # Add more URLs as needed
# ]
# get_shawfloor_products_data(urls, 'vinyl')
