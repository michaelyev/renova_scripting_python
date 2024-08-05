from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def extract_table_data(driver, header_selector, table_selector):
    try:
        data = {}

        # Close any cookie consent banner or overlay if present
        try:
            cookie_banner = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))
            )
            cookie_banner.click()
        except:
            pass  # Ignore if the cookie consent banner is not present

        # Find the header and click it to expand the content
        header = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, header_selector))
        )
        header.click()
        time.sleep(2)  # Give extra time for the content to load

        # Wait for the table to be visible
        table = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, table_selector))
        )

        # Extract data from the table
        rows = table.find_elements(By.TAG_NAME, 'tr')
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) == 2:
                key = cells[0].text.strip().replace(" ", "-").lower()
                value = cells[1].text.strip()
                data[key] = value

        return data
    except Exception as e:
        print(f"Error extracting table data: {e}")
        return {}

if __name__ == "__main__":
    # Set up the Chrome options for headless mode
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    # Initialize the WebDriver with the options
    driver = webdriver.Chrome(options=chrome_options)

    # Open the URL
    driver.get("https://shawfloors.com/flooring/carpet/details/cabana-life-(t)-e9958/stainless")

    # Define the CSS selectors for the header and the table
    header_selector = ".card-header.collapsed#headingOne"
    table_selector = "#full-product-details-specs .specs .table.table-striped"

    # Extract the table data
    table_data = extract_table_data(driver, header_selector, table_selector)

    # Print the extracted data
    for key, value in table_data.items():
        print(f"{key}: {value}")

    # Close the driver
    driver.quit()
