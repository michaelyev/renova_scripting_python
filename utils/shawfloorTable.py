from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def extract_table_data_from_url(driver, header_selector, table_selector):
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

        driver.quit()
        return data
    except Exception as e:
        print(f"Error extracting table data: {e}")
        return {}
