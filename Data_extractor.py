
# To use this code you need to change the numbers in *** line 100 ***.

''' Restart the Chrome driver with the correct preferences before every 
    new grandmaster's directory: We'll set the download directory before 
    processing each grandmaster.

    Ensure that the Chrome download behavior is fully controlled by 
    Selenium: We can reinitialize the driver with updated preferences 
    for each grandmaster to ensure the correct download folder is used.

    Clear default download settings: Ensure that Chrome uses only the paths 
    you specify.'''

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os
import pandas as pd

# Path to your ChromeDriver
chrome_driver_path = '/usr/bin/chromedriver'

# Base directory to store downloaded games
base_download_dir = '/home/arman/Downloads/COS582/Project/grandmasters_games'
if not os.path.exists(base_download_dir):
    os.makedirs(base_download_dir)  # Create base directory if it doesn't exist

# Function to configure Chrome options to set the download directory dynamically
def set_download_directory(gm_download_dir):
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs', {
        "download.default_directory": gm_download_dir,  # Set specific directory for the GM
        "download.prompt_for_download": False,          # Disable download prompts
        "directory_upgrade": True,                      # Automatically overwrite files
        "safebrowsing.enabled": True                    # Enable safe browsing (sometimes needed for downloads)
    })
    return chrome_options

# Function to initialize the Chrome WebDriver
def initialize_driver(download_dir):
    chrome_options = set_download_directory(download_dir)
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to wait for an element to be visible
def wait_for_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, value)))

# Function to scroll until an element is visible
def scroll_to_element(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(2)  # Add a delay after scrolling

# Function to download games from all available pages until there is no "Next" button
def download_games_from_pages(driver, gm_name):
    current_page = 1
    
    while True:
        try:
            # Step 1: Find the checkbox and scroll to it before clicking
            select_all_checkbox = wait_for_element(driver, By.ID, 'master-games-check-all')
            scroll_to_element(driver, select_all_checkbox)
            select_all_checkbox.click()
            time.sleep(1)
            
            # Step 2: Find the download icon and scroll to it before clicking
            download_button = wait_for_element(driver, By.CSS_SELECTOR, 'span.master-games-download-icon')
            scroll_to_element(driver, download_button)
            download_button.click()
            time.sleep(random.uniform(1, 3))  # Random delay after downloading
        except Exception as e:
            print(f"Could not download games for {gm_name} on page {current_page}: {e}")
        
        # Try to go to the next page if it exists
        try:
            next_button = wait_for_element(driver, By.CSS_SELECTOR, 'span.icon-font-chess.ui_pagination-item-icon.chevron-right')
            scroll_to_element(driver, next_button)
            next_button.click()
            time.sleep(random.uniform(3, 5))  # Wait for next page to load
            current_page += 1
        except Exception as e:
            print(f"No more pages for {gm_name} or failed to click Next: {e}")
            break

# Load the CSV file with GM URLs
csv_file_path = '/home/arman/Downloads/COS582/Project/GM_Games_with_URLs.csv'
gm_data = pd.read_csv(csv_file_path)

"""
Select grandmasters from number x (Number in exel - 2) (ex. Garry Kasparov = 2(in exel) - 2 = 0) 
to number y (Number in exel - 1) (ex. Bobby Fischer = 3(in exel) - 1 = 2)
"""
gm_data = gm_data.iloc[0:2]

# Iterate over each grandmaster URL from the specified range in the CSV
for index, row in gm_data.iterrows():
    gm_name = row['GM Name']
    gm_url = row['GM URL']
    
    # Create a directory for each grandmaster
    gm_download_dir = os.path.join(base_download_dir, gm_name.replace(" ", "_"))  # Replace spaces with underscores
    if not os.path.exists(gm_download_dir):
        os.makedirs(gm_download_dir)

    # Initialize a new Chrome driver for each grandmaster with their specific download directory
    driver = initialize_driver(gm_download_dir)
    
    try:
        # Open the grandmaster's page from the CSV URL
        driver.get(gm_url)
        time.sleep(random.uniform(4, 8))  # Wait for the page to load
        
        # Download games from up to 5 pages
        download_games_from_pages(driver, gm_name)
        
    except Exception as e:
        print(f"Error occurred while processing {gm_name}: {e}")
    
    # Close the browser for the current grandmaster before moving to the next one
    driver.quit()
    
    # Optional: Add a delay before moving to the next grandmaster
    time.sleep(random.uniform(2, 3))

print("Grandmaster games for GM number x to y have been downloaded into individual directories.")
