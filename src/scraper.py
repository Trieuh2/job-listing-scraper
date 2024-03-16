import json
import math
from time import sleep
from random import randint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import utils

class Scraper:
    def __init__(self, url):
        self.driver = webdriver.Chrome()
        self.url = url
        
        # Initialize the Scraper based on the configuration file
        with open('config.json') as config_file:
            config = json.load(config_file)

        self.excluded_keywords = config['excluded_keywords']
        self.csv_headers = config['csv_settings']['csv_headers']
        self.crawl_delay = config['crawl_delay']
        self.jobs = utils.read_jobs_excel(config['csv_settings']['excel_output_path']) # {hash_id : record}
        self.initial_num_records = len(self.jobs)
        self.search_criteria = '|'.join(list(config['indeed_criteria'].values()))
        self.previous_page_hash_ids = set()

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
        current_page_added_hash_ids = set()
        job_cards = self.driver.find_elements(By.CSS_SELECTOR, 'div.job_seen_beacon')

        for job_card in job_cards:
            add_to_results = True

            try:
                job_details = {}

                # Get job_link and hash_id first
                title_anchor_element = job_card.find_element(By.TAG_NAME, 'a')
                indeed_full_url = title_anchor_element.get_attribute('href')
                job_details['job_link'] = utils.parse_indeed_url(indeed_full_url)
                job_details['hash_id'] = utils.string_to_hash(job_details['job_link'])
                hash_id = job_details['hash_id']

                description_element = job_card.find_element(By.CSS_SELECTOR, 'tr.underShelfFooter')
                description = description_element.text if description_element else 'N/A'
                job_details['description'] = description
                
                # Validate the structure of the job_url and whether the user's configured years of experience meets the minimum on the job description
                if not utils.is_valid_indeed_job_link(job_details['job_link']) or not utils.is_valid_description_criteria(description):
                    add_to_results = False

                for header in self.csv_headers:
                    if not add_to_results:
                        break

                    if header == 'title':
                        title_element = job_card.find_element(By.CSS_SELECTOR, 'h2.jobTitle')
                        job_details[header] = title_element.text if title_element else 'Title not found'

                        if title_element and utils.exclude_based_on_title(self.excluded_keywords, title_element.text):
                            add_to_results = False

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

                    elif header == 'posted_date':
                        posted_date_element = job_card.find_element(By.CSS_SELECTOR, 'span[data-testid="myJobsStateDate"]')
                        job_details[header] = utils.parse_post_date(posted_date_element.text)

                    elif header == 'applied':
                        # Fetch pre-existing values or default to "No", for not applied to job yet
                        if hash_id in self.jobs:
                            job_details[header] = self.jobs[hash_id][header]
                        else:
                            job_details[header] = 'No'

                    elif header == 'search_criteria':
                        job_details[header] = self.search_criteria

                if add_to_results:
                    # Update results
                    self.jobs[hash_id] = job_details
                    current_page_added_hash_ids.add(hash_id)

                    # Print the details
                    print('\n'.join([f'{header}: {job_details[header]}' for header in self.csv_headers]))
                    print('\n')
            except NoSuchElementException as e:
                print(f"An element was not found: {e}")
        return current_page_added_hash_ids
    
    def navigate_next_page(self):
        self.url = utils.get_next_page_url(self.url)
        sleep(randint(self.crawl_delay, math.floor(self.crawl_delay * 1.5)))
        self.driver.get(self.url)
        return
        
    def shutdown(self):
        self.driver.quit()
        return