import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from bs4 import BeautifulSoup
import process.constants as const

# Path to your chromedriver
CHROMEDRIVER_PATH = r"C:\Drivers\chromedriver.exe"

# Initialize the WebDriver
service = Service(CHROMEDRIVER_PATH)
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get(const.BASE_URL)
    wait = WebDriverWait(driver, 10)
    driver.maximize_window()

    # Wait for the LinkedIn sign-in button to be clickable and then click
    linkedin_button = wait.until(
        EC.element_to_be_clickable((By.CLASS_NAME, "nav__button-secondary.btn-md.btn-secondary-emphasis")))
    linkedin_button.click()

    # Wait for email input field, clear it and enter email
    login_email = wait.until(EC.visibility_of_element_located((By.ID, "username")))
    login_email.send_keys(const.EMAIL)

    # Wait for password input field, clear it and enter password
    login_password = wait.until(EC.visibility_of_element_located((By.ID, "password")))
    login_password.send_keys(const.PASSWORD)

    # Click on the next button after entering the password
    login_next_button = wait.until(
        EC.element_to_be_clickable((By.CLASS_NAME, "btn__primary--large.from__button--floating")))
    login_next_button.click()

    # Wait for the profile page to load completely
    time.sleep(10)

    # Navigate to the search results page
    driver.get(const.SEARCH_URL)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'reusable-search__result-container')))

    companies_dict = {}  # Dictionary to store unique companies

    # Limit to scraping first 3 pages
    page_count = 0
    while page_count < 3:
        page_count += 1
        print(f"Scraping page {page_count}")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        company_cards = soup.find_all('li', {'class': 'reusable-search__result-container'})

        for company in company_cards:
            try:
                # Get the company link and click on it
                company_link = company.find('a', {'class': 'app-aware-link'})['href']
                driver.get(company_link)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'org-top-card-summary-info-list__info-item')))

                # Check if the company location is Hyderabad
                company_soup = BeautifulSoup(driver.page_source, 'html.parser')
                location_elements = company_soup.find_all('div', {'class': 'org-top-card-summary-info-list__info-item'})

                # Assuming second element contains location info (adjust if needed)
                if len(location_elements) >= 2 and 'Hyderabad' in location_elements[1].text:
                    # Extract company name
                    company_name_element = company_soup.find('h1', {'class': 'org-top-card-summary__title'})
                    company_name = company_name_element.text.strip() if company_name_element else 'Not specified'
                    print(company_name)

                    industry_element = company_soup.find('div', {'class': 'org-top-card-summary-info-list__info-item'})
                    industry = industry_element.text.strip() if industry_element else 'Not specified'
                    print(industry)

                    # Extract number of employees
                    employee_element = company_soup.find("a", {'class': 'ember-view org-top-card-summary-info-list__info-item'})
                    no_of_employees = employee_element.text.strip() if employee_element else 'Not specified'
                    print(no_of_employees)

                    # about_button = wait.until(
                    #                 EC.element_to_be_clickable((By.CLASS_NAME, "ember-view pv3 ph4 t-16 t-bold t-black--light org-page-navigation__item-anchor ")))
                    # about_button.click()
                    # time.sleep(5)

                    # website_element = company_soup.find('a', {'class': 'link-without-visited-state ember-view'})
                    # company_website = website_element['href'] if website_element else 'Not specified'

                    # Check if company already exists in dictionary
                    if company_name in companies_dict:
                        # Update existing entry
                        companies_dict[company_name] = {
                            'Company Name': company_name,
                            'Industry': industry,
                            'No of Employees': no_of_employees,
                            # 'Website': company_website
                        }
                    else:
                        # Add new entry
                        companies_dict[company_name] = {
                            'Company Name': company_name,
                            'Industry': industry,
                            'No of Employees': no_of_employees,
                            # 'Website': company_website
                        }

                    print(f"Added company: {company_name}")

                # Go back to the search results
                driver.back()
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'reusable-search__result-container')))

            except Exception as e:
                print(f"An error occurred while processing company: {e}")
                continue

        # Write the data to a CSV file
        csv_file = 'company_data.csv'
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['Company Name', 'Industry', 'No of Employees'])
            writer.writeheader()
            for company_info in companies_dict.values():
                writer.writerow(company_info)
        print(f"Data has been written to {csv_file}")

        # Scrolls to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Check if there's a next page
        try:
            next_button = driver.find_element(By.XPATH, '//button[@aria-label="Next"]')
            wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Next"]')))
            next_button.click()
            print("Navigating to next page")
            time.sleep(5)  # Add a short delay to allow the page to load
        except TimeoutException:
            print("No more pages")
            break


except TimeoutException as e:
    print(f"Timeout occurred: {e}")
except NoSuchElementException as e:
    print(f"Element not found: {e}")
except WebDriverException as e:
    print(f"WebDriverException occurred: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    # Close the driver
    driver.quit()
