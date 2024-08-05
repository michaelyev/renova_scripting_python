import os
import requests
import json
from urllib.parse import urlencode
import time

def fetch_json_from_api(style_number, color_number, product_type_code, product_group_name, unique_param, proxies):
    url = "https://shawfloors.com/api/odata/Vignettes"
    params = {
        'styleNumber': f"'{style_number}'",
        'colorNumber': f"'{color_number}'",
        'productTypeCode': f"'{product_type_code}'",
        'productGroupPermanentName': f"'{product_group_name}'",
        '_': unique_param  # This could be a timestamp or any unique identifier
    }

    # Construct the full URL with encoded parameters
    full_url = f"{url}?{urlencode(params)}"
    print(f"Full URL: {full_url}")

    # Make the GET request to the API with retry logic
    max_retries = 3
    for retry in range(max_retries):
        try:
            response = requests.get(full_url, proxies=proxies)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to retrieve data. Status code: {response.status_code}")
                time.sleep(1)  # Wait before retrying
        except Exception as e:
            print(f"Error fetching data from API: {e}")
            time.sleep(1)  # Wait before retrying
    return None

def download_image(image_url, image_name, save_directory='images', proxies=None):
    try:
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(image_url, headers=headers, stream=True, proxies=proxies)
        if response.status_code == 200:
            image_path = os.path.join(save_directory, image_name)
            with open(image_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            return image_name
        else:
            print(f"Failed to retrieve the image. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

def process_api_response(response, style_number, color_number, save_directory='images'):
    image_data = []
    
    if 'value' in response:
        for item in response['value']:
            vignette_name = item['VignetteName']
            image_url = f"https://img.shawinc.com/s7/is/image/ShawIndustries/?src=ir(ShawIndustriesRender/{vignette_name}?res=20&src=is(ShawIndustriesRender/{style_number}_{color_number}_MAIN))&fit=crop,0&qlt=80&wid=590&hei=590"
            image_name = f"{vignette_name}.jpg"  # Ensure we have a proper filename
            
            downloaded_image_name = download_image(image_url, image_name, save_directory)
            
            if downloaded_image_name:
                image_data.append({
                    'vignette_name': vignette_name,
                    'image_url': image_url,
                    'image_name': downloaded_image_name
                })
    
    return image_data

def save_image_data_to_json(image_data, filename='direct.json'):
    with open(filename, 'w') as json_file:
        json.dump(image_data, json_file, indent=4)

# Example usage
if __name__ == "__main__":
    style_number = 'cc80b'
    color_number = '00307'
    product_type_code = '2'
    product_group_name = 'shawfloors'
    unique_param = '1717743243540'
    proxies = {
        'http': 'http://jawad024:ZsvM_sKT=UN7zxg@pr.oxylabs.io:7777',
        'https': 'https://jawad024:ZsvM_sKT=UN7zxg@pr.oxylabs.io:7777',
    }
    
    api_response = fetch_json_from_api(style_number, color_number, product_type_code, product_group_name, unique_param, proxies)
    
    if api_response:
        image_data = process_api_response(api_response, style_number, color_number)
        save_image_data_to_json(image_data)
        print("Images downloaded and data saved to direct.json")
    else:
        print("Failed to fetch API response.")
