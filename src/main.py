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

    indeed_criteria = config['indeed_criteria']
    indeed_url = utils.build_indeed_url(
        max_days_posted_ago = indeed_criteria['max_days_posted_ago'],
        position            = indeed_criteria['position'],
        experience_level    = indeed_criteria['experience_level'],
        job_type            = indeed_criteria['job_type'],
        location            = indeed_criteria['location']
    )

    # Set up and run the Scraper
    scraper = Scraper(indeed_url)
    scraper.scrape_num_pages(config['num_pages_to_scrape'])

    if config['update_csv_on_completion']:
        utils.write_jobs_csv(config['csv_output_path'], scraper.jobs)