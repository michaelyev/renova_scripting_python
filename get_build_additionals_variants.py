import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import requests

def download_image(url, folder_path, image_name):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        with open(os.path.join(folder_path, image_name), 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {image_name} in {folder_path}")
    except Exception as e:
        print(f"Error downloading {image_name}: {e}")

def get_model_from_image(url):
    try:
        parts = url.split('-')
        if len(parts) >= 3:
            extracted_text = parts[-2]
            return extracted_text
        else:
            print(f"URL does not contain enough parts: {url}")
            return None
    except Exception as e:
        print(f"Error extracting model from image URL: {e}")
        return None

def get_build_additionals_variants():
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        url = 'https://www.build.com/kohler-k-99259/s1087923?uid=2612769&searchId=5xEncLKerd'
        driver.get(url)
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.ma0.pa0")))

        ul_element = driver.find_element(By.CSS_SELECTOR, "ul.ma0.pa0")

        if not ul_element:
            print("No ul element with classes 'ma0' and 'pa0' found")
        else:
            extracted_data = []
            
            li_elements = ul_element.find_elements(By.CSS_SELECTOR, 'li')

            for li_element in li_elements:
                try:
                    h3_element = li_element.find_element(By.CSS_SELECTOR, 'h3.tc1-title')
                    section_title = h3_element.text
                    section_key = section_title.lower().replace(' ', '_')

                    button_elements = li_element.find_elements(By.CSS_SELECTOR, 'button .qdzeh')
                    
                    for button_element in button_elements:
                        data_obj = {}

                        try:
                            img_element = button_element.find_element(By.CSS_SELECTOR, 'img')
                            img_src = img_element.get_attribute('src')
                            match = re.search(r'/([^/]+)/([^/]+)_productimage\d+\.(?:jpg|jpeg|png|gif)$', img_src)
                            print(img_src)
                            print(match)
                            if match:
                                extracted_text = match.group(1)
                                model_name = get_model_from_image(img_src)
                                if model_name:
                                    data_obj['model'] = model_name
                                    data_obj['img'] = img_src

                                    # Download the image
                                    folder_path = os.path.join('products', 'sinks', model_name, 'variants')
                                    os.makedirs(folder_path, exist_ok=True)
                                    img_name = f'image_{len(extracted_data) + 1}.jpg'  # Unique name for each image
                                    download_image(img_src, folder_path, img_name)

                                    # Append data object to extracted_data
                                    extracted_data.append(data_obj)
                                else:
                                    print(f"Failed to extract model from image URL: {img_src}")
                        except NoSuchElementException:
                            continue

                except NoSuchElementException:
                    continue

            print("Extracted data:", extracted_data)

    except Exception as e:
        print("An error occurred:", e)

    finally:
        driver.quit()

get_build_additionals_variants()
