from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from random import randint
import utils


class Scraper:
    def __init__(self, url, excluded_keywords, csv_headers, csv_output_path):
        self.driver = webdriver.Chrome()
        self.url = url
        self.excluded_keywords = excluded_keywords
        self.jobs = utils.read_jobs_csv(csv_output_path) # {hash_id : record}
        self.csv_headers = csv_headers
        self.driver.get(self.url)

    def extract_current_page(self):
        # Wait for job cards to load with a maximum of 5 tries
        max_tries = 5

        for attempt in range(max_tries):
            try:
                wait = WebDriverWait(self.driver, 5)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.job_seen_beacon')))
                break  # If successful, break out of the loop
            except TimeoutException:
                if attempt < max_tries - 1:
                    print(f"Timeout encountered on attempt {attempt + 1}, refreshing the page and retrying...")
                    self.driver.refresh()
                else:
                    print(f"Failed to load the page after {max_tries} attempts. Proceeding with the next steps.")
                    return

        # Extract and print job details
        job_cards = self.driver.find_elements(By.CSS_SELECTOR, 'div.job_seen_beacon')

        for job_card in job_cards:
            add_to_results = True

            try:
                job_details = {}

                for header in self.csv_headers:
                    if header == 'title':
                        title_element = job_card.find_element(By.CSS_SELECTOR, 'h2.jobTitle')
                        job_details[header] = title_element.text if title_element else 'Title not found'

                        if title_element and utils.exclude_based_on_title(self.excluded_keywords, title_element.text):
                            add_to_results = False
                            break
                    elif header == 'company':
                        company_element = job_card.find_element(By.CSS_SELECTOR, 'span[data-testid="company-name"]')
                        job_details[header] = company_element.text if company_element else 'Company not found'

                    elif header == 'location':
                        location_element = job_card.find_element(By.CSS_SELECTOR, 'div[data-testid="text-location"]')
                        job_details[header] = location_element.text if location_element else 'Location not found'

                    elif header == 'salary_preview':
                        try:
                            salary_snippet_container = job_card.find_element(By.CSS_SELECTOR, '[class*="salary-snippet-container"]')
                            salary_element = salary_snippet_container.find_element(By.CSS_SELECTOR, 'div[data-testid="attribute_snippet_testid"]')
                            job_details[header] = salary_element.text if salary_element else 'N/A'
                        except NoSuchElementException as e:
                            job_details[header] = 'N/A'

                    elif header == 'job_link':
                        title_anchor_element = job_card.find_element(By.TAG_NAME, 'a')
                        indeed_full_url = title_anchor_element.get_attribute('href')
                        job_details[header] = utils.parse_indeed_url(indeed_full_url)

                    elif header == 'posted_date':
                        posted_date_element = job_card.find_element(By.CSS_SELECTOR, 'span[data-testid="myJobsStateDate"]')
                        job_details[header] = utils.parse_post_date(posted_date_element.text)

                if add_to_results:
                    hash_id = utils.string_to_hash(job_details['job_link'])
                    job_details['hash_id'] = hash_id 

                    # Update results
                    self.jobs[hash_id] = job_details

                    # Print the details
                    print('\n'.join([f'{header}: {job_details[header]}' for header in self.csv_headers]))
                    print('\n')
            except NoSuchElementException as e:
                print(f"An element was not found: {e}")
        return
    
    def navigate_next_page(self):
        self.url = utils.get_next_page_url(self.url)
        sleep(randint(2,4)) # Crawl delay
        self.driver.get(self.url)
        return
        
    def shutdown(self):
        self.driver.quit()
        return
    
    def scrape_num_pages(self, num_pages_to_scrape):
        for _ in range(num_pages_to_scrape):
            self.extract_current_page()
            self.navigate_next_page()

        self.shutdown()
        return
