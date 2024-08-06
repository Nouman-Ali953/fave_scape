from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import os

# Initialize WebDriver
driver_path = "C:/Users/nauma/Downloads/chromedriver-win64/chromedriver.exe"  # Update this with the path to your WebDriver
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

file_path = 'scraped_data.xlsx'

# Main URL for initial scraping
homepage_url = 'https://myfave.com/'  # Replace this with the actual homepage URL

# Function to scrape anchor tags from sections with class 'mt-8'
def scrape_homepage_anchors():
    # Wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    
    # Get the page source and parse it with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Find all sections with class 'mt-8'
    sections = soup.find_all('section', class_='mt-8')
    
    all_anchors = []
    
    for section in sections:
        # Find the category from the h3 tag
        category_tag = section.find('h3')
        if category_tag:
            category = category_tag.get_text(strip=True)
        
        # Find all anchor tags within the section
        anchor_tags = section.find_all('a')
        
        # Extract href attributes and add to list with category
        for tag in anchor_tags:
            href = tag.get('href')
            if href:
                full_url = f"https://myfave.com{href}"
                all_anchors.append((category, full_url))
    
    return all_anchors

# Function to change city
def change_city(city_name):
    try:
        # Click on the button with span class 'truncate' to open the popup
        change_city_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[span[@class="truncate"]]'))
        )
        change_city_button.click()

        # Wait for the popup with the "Change City" button to appear
        change_city_popup_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Change city")]'))
        )
        change_city_popup_button.click()

        # Select the city from the dropdown or city list within the popup
        city_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f'//a[contains(text(), "{city_name}")]'))
        )
        city_option.click()
        
        # Wait for the page to load after changing the city
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "some-unique-class-after-page-load")]')))
        
    except Exception as e:
        print(f'Error: {e}')

# Scrape data for a list of cities
def scrape_multiple_cities(cities):
    all_anchors = []
    for city in cities:
        try:
            # Go to the homepage URL
            driver.get(homepage_url)
            
            # Change to the specified city
            change_city(city)
            
            # Scrape anchor tags from sections with class 'mt-8'
            city_anchors = scrape_homepage_anchors()
            all_anchors.extend(city_anchors)
            
            # Print message
            print(f'Scraped data for city: {city}')
            
        except Exception as e:
            print(f'Error while scraping city {city}: {e}')
    
    return all_anchors

# List of cities to scrape
cities = [
   'Singapore' 
    # Add more cities as needed
]

# Collect all data
all_anchors = scrape_multiple_cities(cities)

# Convert all data to DataFrame and save/append to Excel
if all_anchors:
    df = pd.DataFrame(all_anchors, columns=['Category', 'URL'])
    if not os.path.isfile(file_path):
        df.to_excel(file_path, index=False)
    else:
        existing_df = pd.read_excel(file_path)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df.to_excel(file_path, index=False)
    print(f'All data saved to {file_path}')

# Close the WebDriver
driver.quit()
