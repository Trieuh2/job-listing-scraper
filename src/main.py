import os
import json
import utils
from scraper import Scraper

if __name__ == '__main__':
    # Clear console
    os.system('cls' if os.name == 'nt' else 'clear')

    # Load configurations
    with open('config.json') as config_file:
        config = json.load(config_file)

    indeed_url_params = config['indeed_url_params']
    indeed_url = utils.build_indeed_url(
        max_days_posted_ago = indeed_url_params['max_days_posted_ago'],
        position            = indeed_url_params['position'],
        experience_level    = indeed_url_params['experience_level'],
        job_type            = indeed_url_params['job_type'],
        location            = indeed_url_params['location']
    )

    excluded_keywords           = set(config['excluded_keywords'])
    csv_output_path             = config['csv_output_path']
    csv_headers                 = config['csv_headers']
    num_pages_to_scrape         = config['num_pages_to_scrape']
    update_csv_on_completion    = config['update_csv_on_completion']

    # Set up and run the Scraper
    scraper = Scraper(indeed_url, excluded_keywords, csv_headers, csv_output_path)
    scraper.scrape_num_pages(num_pages_to_scrape)

    if update_csv_on_completion:
        utils.write_jobs_csv(csv_output_path, scraper.jobs)