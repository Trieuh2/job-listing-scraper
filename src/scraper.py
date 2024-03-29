import json
import logging
import math
from random import randint
from time import sleep
from typing import Dict, Set, Tuple

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

import utils

class Scraper:
    """A web scraper for extracting job listings.

    Attributes:
        driver (webdriver.Chrome): The Selenium web driver for Chrome.
        url (str): The URL to scrape.
        excluded_keywords (Set[str]): Keywords to exclude from the results.
        csv_headers (List[str]): Headers for the CSV output.
        crawl_delay (int): Delay between page crawls.
        jobs (Dict[str, Dict[str, str]]): Dictionary of job listings.
        initial_num_records (int): Initial number of job records.
        num_errored_job_extractions (int): Number of job extractions that resulted in errors.
        search_criteria (str): Criteria used for searching jobs.
        previous_page_hash_ids (Set[str]): Hash IDs of job listings from the previous page.
        logger (logging.Logger): Logger for the scraper.
    """

    def __init__(self, url):
        """Initialize the Scraper with a URL.

        Args:
            url (str): The URL to scrape.
        """
        self.driver = webdriver.Chrome()
        self.url = url
        self.initialize_scraper()
    
    def initialize_scraper(self) -> None:
        """
        Initialize the Scraper based on the configuration file.
        
        Returns:
            None
        """
        with open('config.json') as config_file:
            config = json.load(config_file)

        self.excluded_keywords = config['excluded_keywords']
        self.csv_headers = config['csv_settings']['csv_headers']
        self.crawl_delay = config['crawl_delay']
        self.jobs = utils.read_jobs_excel(config['csv_settings']['excel_output_path'])  # {hash_id: record}
        self.initial_num_records = len(self.jobs)
        self.num_errored_job_extractions = 0
        self.search_criteria = '|'.join(list(config['indeed_criteria'].values()))
        self.previous_page_hash_ids = set()
        self.logger = logging.getLogger(__name__)
        self.driver.get(self.url)

    def extract_current_page(self) -> Set[str]:
        """Extract and print job details from the current page.

        Returns:
            Set[str]: Set of hash IDs for the jobs added to the results.
        """
        current_page_added_hash_ids = set()
        success, message = self.wait_for_job_cards_to_load()

        if not success:
            print(message)
            return current_page_added_hash_ids

        # Wait 1s to allow any dynamic web page changes to occur before scraping
        sleep(1)
        job_cards = self.driver.find_elements(By.CSS_SELECTOR, 'div.job_seen_beacon')

        for job_card in job_cards:
            self.process_job_card(job_card, current_page_added_hash_ids)

        return current_page_added_hash_ids

    def process_job_card(self, job_card: WebElement, current_page_added_hash_ids: Set[str]) -> None:
        """Process an individual job card.

        Args:
            job_card (WebElement): The job card element.
            current_page_added_hash_ids (Set[str]): Set of hash IDs for the jobs added to the results.
        """
        add_to_results = True
        job_details = {}

        try:
            # Extract job details
            title_anchor_element = job_card.find_element(By.TAG_NAME, 'a')
            indeed_full_url = title_anchor_element.get_attribute('href')

            if indeed_full_url is None:
                add_to_results = False
                self.num_errored_job_extractions += 1
                return

            job_details['job_link'] = utils.parse_indeed_url(indeed_full_url)
            job_details['hash_id'] = utils.string_to_hash(job_details['job_link'])
            hash_id = job_details['hash_id']

            description_element = job_card.find_element(By.CSS_SELECTOR, 'tr.underShelfFooter')
            description = description_element.text if description_element else 'N/A'
            job_details['description'] = description

            # Validate the job details
            if not utils.is_valid_indeed_job_link_structure(job_details['job_link']) or not utils.description_has_valid_years_of_experience(description):
                add_to_results = False

            for header in self.csv_headers:
                if not add_to_results:
                    break

                add_to_results = self.extract_job_detail(job_card, job_details, header, hash_id)

                if header not in job_details:
                    job_details[header] = ''

            if add_to_results:
                # Update results and print details
                self.jobs[hash_id] = job_details
                current_page_added_hash_ids.add(hash_id)
                print('\n'.join([f'{header}: {job_details[header]}' for header in self.csv_headers]), '\n')

        except NoSuchElementException as e:
            print(f"An element was not found: {e}")
    
    def extract_job_detail(self, job_card: WebElement, job_details: Dict[str, str], header: str, hash_id: str) -> bool:
        """
        Extracts specific job details based on the header provided and updates the job_details dictionary.

        Args:
            job_card (WebElement): The WebElement representing a job card.
            job_details (Dict[str, str]): The dictionary to store job details, where the key is the header and the value is the corresponding detail.
            header (str): The specific job detail to extract, such as 'title', 'company', 'location', etc.
            hash_id (str): The unique identifier for the job.

        Returns:
            bool: True if the job detail is successfully extracted and added to job_details, False otherwise.
        """
        try:
            if header == 'title':
                title_element = job_card.find_element(By.CSS_SELECTOR, 'h2.jobTitle')
                job_details[header] = title_element.text if title_element else 'Title not found'

                if title_element and utils.exclude_based_on_title(self.excluded_keywords, title_element.text):
                    return False  # Do not add to results if title is excluded

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
                except NoSuchElementException:
                    job_details[header] = 'N/A'

            elif header == 'posted_date':
                posted_date_element = job_card.find_element(By.CSS_SELECTOR, 'span[data-testid="myJobsStateDate"]')
                scraped_date_str = utils.parse_post_date(posted_date_element.text)

                if hash_id in self.jobs:
                    job_details[header] = str(self.jobs[hash_id][header])
                else:
                    job_details[header] = scraped_date_str

            elif header == 'applied':
                # Fetch pre-existing values or default to "No", for not applied to job yet
                if hash_id in self.jobs:
                    job_details[header] = str(self.jobs[hash_id][header])
                else:
                    job_details[header] = 'No'

            elif header == 'search_criteria':
                job_details[header] = self.search_criteria

            return True  # By default, add to results
        except:
            self.num_errored_job_extractions += 1
            return False

    def wait_for_job_cards_to_load(self, wait_time: int=5, max_tries: int=5) -> Tuple[bool, str]:
        """
        Waits for job cards to load on the webpage.

        Args:
            wait_time (int, optional): The maximum number of seconds to wait for each attempt. Defaults to 5.
            max_tries (int, optional): The maximum number of attempts to wait for the job cards to load. Defaults to 5.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating whether the job cards were successfully loaded and a message describing the outcome.
        """
        for attempt in range(max_tries):
            try:
                wait = WebDriverWait(self.driver, wait_time)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.job_seen_beacon')))
                return (True, f"Job cards loaded successfully on attempt {attempt + 1}.")
            except TimeoutException:
                if attempt < max_tries - 1:
                    self.logger.warning(f"Timeout encountered on attempt {attempt + 1}, refreshing the page and retrying...")
                    self.driver.refresh()
                else:
                    return (False, f"Failed to load the job cards after {max_tries} attempts.")
        return (False, f"Failed to load the job cards after {max_tries} attempts.")

    def navigate_next_page(self) -> None:
        """
        Navigates to the next page of job listings by updating the current URL to the next page's URL.

        Returns:
            None
        """
        self.url = utils.get_next_page_url(self.url)
        sleep(randint(self.crawl_delay, math.floor(self.crawl_delay * 1.5)))
        self.driver.get(self.url)
        
    def shutdown(self) -> None:
        """
        Shuts down the web driver, closing all associated windows and terminating the driver process.

        Returns:
            None
        """
        self.driver.quit()