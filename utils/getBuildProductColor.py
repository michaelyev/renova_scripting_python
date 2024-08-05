import os
import json

def load_data(folder_name, categories):
    # Nested dictionary to store data from each category and color
    data_dict = {category: {} for category in categories}
    
    # Process each category
    for category in categories:
        category_folder = os.path.join(folder_name, category)
        
        # Get a list of all JSON files in the category folder
        json_files = [f for f in os.listdir(category_folder) if f.endswith('.json')]
        
        # Process each JSON file
        for json_file_name in json_files:
            file_path = os.path.join(category_folder, json_file_name)
            
            # Load the JSON file
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
                
                # Extract color from the file name
                parts = json_file_name.split('-')
                if len(parts) > 2:
                    color = '-'.join(parts[1:-1])
                else:
                    color = parts[1]
                
                # Store data in nested dictionary
                data_dict[category][color] = data
    
    return data_dict

def find_color_by_url(data_dict, url):
    # Iterate through each category and color
    for category, colors in data_dict.items():
        for color, links in colors.items():
            # Check if the URL is a substring of any link
            if any(url in link for link in links):
                return category, color
    
    return None, None

# Load data globally so it can be accessed directly when imported
folder_name = 'utils/buildColorProducts'
categories = ['vanities', 'doors', 'tiles', 'sinks', 'faucets']
data_dict = load_data(folder_name, categories)

def get_color_for_url(url):
    link = url.split('searchId=')[0]
    # Use the global data_dict to find the color for the given URL
    result = find_color_by_url(data_dict, link)
    return result[1] if result else None

