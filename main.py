import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Set up the WebDriver (ensure ChromeDriver is installed and in PATH)
driver = webdriver.Chrome()

# Open the URL for past launches
url = 'https://nextspaceflight.com/launches/past/'  # Updated URL for past launches
driver.get(url)

# Allow time for the page to load completely
time.sleep(5)

# Define CSV column headers
headers = ['Company', 'Mission', 'Launch Pad', 'Date', 'Time', 'Details URL', 'Watch URL']

# Initialize a list to hold all the launch data
launch_data = []


# Function to scrape the launch data from a page
def scrape_page():
    launch_blocks = driver.find_elements(By.XPATH, "//div[contains(@class, 'launch')]")

    for i, launch in enumerate(launch_blocks):
        try:
            # Extract the company name
            try:
                company = launch.find_element(By.XPATH, ".//div[contains(@class, 'mdl-card__title-text')]").text.strip()
            except NoSuchElementException:
                company = "Unknown"

            # Extract the mission name
            try:
                mission = launch.find_element(By.XPATH, ".//h5").text.strip()
            except NoSuchElementException:
                mission = "Unknown"

            # Extract the launch pad location
            try:
                location = launch.find_element(By.XPATH, ".//div[@class='mdl-card__supporting-text']").text.split("\n")[1].strip()
            except NoSuchElementException:
                location = "Unknown"

            # Extract date and time of the launch
            try:
                datetime_text = launch.find_element(By.XPATH, ".//span[contains(@id, 'localized')]").text.strip()
                date_time_parts = datetime_text.split(" ")
                date = " ".join(date_time_parts[:4])  # Example: "Sat Aug 31, 2024"
                time_of_launch = " ".join(date_time_parts[4:])  # Example: "2:48 AM GMT-6"
            except (NoSuchElementException, ValueError, IndexError):
                date = "Unknown"
                time_of_launch = "Unknown"

            # Extract the Details URL
            try:
                details_url = launch.find_element(By.XPATH, ".//a[contains(@href, '/launches/details')]").get_attribute('href')
            except NoSuchElementException:
                details_url = "Unknown"

            # Extract the Watch URL
            try:
                watch_url = launch.find_element(By.XPATH, ".//a[contains(@href, 'youtube') or contains(@href, 'spacex')]").get_attribute('href')
            except NoSuchElementException:
                watch_url = "Unknown"

            # Append the launch data to the list
            launch_data.append([company, mission, location, date, time_of_launch, details_url, watch_url])

        except Exception as e:
            print(f"Error extracting data from launch {i + 1}: {e}")
            continue


# Function to click the "Next" button and go to the next page
def go_to_next_page():
    try:
        next_button = driver.find_element(By.XPATH, "//a[@class='mdc-button mdc-button--raised' and contains(., 'next')]")
        next_button.click()
        time.sleep(5)  # Add a delay to let the page load
        return True
    except NoSuchElementException:
        print("No more pages or 'Next' button not found.")
        return False


# Start scraping and continue until there are no more pages
page = 1
while True:
    print(f"Scraping page {page}...")
    scrape_page()

    # Try to go to the next page; if there's no next button, break the loop
    if not go_to_next_page():
        break

    page += 1

# Insert the headers at the top
launch_data.insert(0, headers)

# Define the CSV file path
csv_file_path = 'space_launches.csv'

# Write the data to the CSV file
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(launch_data)

print(f"Scraping complete. Data saved to {csv_file_path}.")

# Close the browser
driver.quit()
