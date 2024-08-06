from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import time

# Set up Chrome driver service
service = Service('C:/Users/nauma/Downloads/chromedriver-win64/chromedriver.exe')  # Change this to the path of your ChromeDriver

# Initialize the WebDriver
driver = webdriver.Chrome(service=service)

# List of URLs to scrape
excel_file = 'scraped_data.xlsx'  # Change this to the path of your Excel file
df = pd.read_excel(excel_file)
urls = df['URL'].tolist()  # Assumes the column containing URLs is named 'URL'

data = []

for url in urls:
    try:
        print(f"Processing URL: {url}")
        driver.get(url)

        # Wait until the title element is present
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h2.truncate.text-base.font-semibold.underline"))
            )
            print("Title element is present.")
        except Exception as e:
            print(f"Error waiting for title element: {e}")
            continue

        # Get the page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        title = soup.find("h2", class_='truncate text-base font-semibold underline')
        address = soup.find("span", class_='line-clamp-1 underline decoration-from-font underline-offset-2')
        city = soup.find("div", class_='truncate text-sm font-normal text-muted-foreground')

        # Extract main page data
        main_data = {
            'Title': title.text.strip() if title else 'Title not found',
            'Address': address.text.strip() if address else 'Address not found',
            'City': city.text.strip() if city else 'City not found',
            'Country': 'Singapore',
            'Category': 'Eat & Beauty',
            'Outlets': []
        }

        print(f"Main Data Extracted: {main_data}")

        try:
            # Click the element to open the popup
            span_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.shrink-0"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", span_element)
            time.sleep(1)  # Wait for the scrolling to complete
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "span.shrink-0"))
            ).click()

            # Wait for the popup to appear
            popup_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.h-full.flex-1.overflow-y-auto.px-6.py-8"))  # Replace with actual popup container selector if necessary
            )

            # Extract the h6 and span tags from the popup
            h6_elements = WebDriverWait(popup_container, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h6.line-clamp-1.text-sm.font-extrabold"))
            )
            span_elements = WebDriverWait(popup_container, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.line-clamp-1"))  # Replace with the correct selector if necessary
            )

            if not h6_elements or not span_elements:
                print("No outlets found.")
            else:
                for h6, span in zip(h6_elements, span_elements):
                    outlet_info = {
                        'Outlet': h6.text.strip(),
                        'Details': span.text.strip()
                    }
                    main_data['Outlets'].append(outlet_info)

            print(f"Outlets Data Extracted: {main_data['Outlets']}")

        except TimeoutException:
            print("Timed out waiting for popup or outlet elements.")
        except NoSuchElementException:
            print("No such element found for popup or outlet.")

        data.append(main_data)
        print(f"Main Data for URL {url}: {main_data}")

        # Pause to be respectful to the server
        time.sleep(2)

    except Exception as e:
        print(f"Failed to process {url}: {e}")

# Convert data to a DataFrame and save to Excel
df = pd.DataFrame(data)
df.to_excel('singapore_with_outlets.xlsx', index=False)

# Close the WebDriver
driver.quit()
print("Web scraping completed and data saved to main_page_data_with_outlets.xlsx.")
