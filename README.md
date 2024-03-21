# Job Listing Scraper

This application scrapes Indeed job results and parses the data into a working Excel spreadsheet that users can use for their job search.

## Usage

![Screenshot of Feature X](./screenshots/gui.png)

## Features

- User-friendly GUI implemented via customTkinter
- Searching jobs using Position, Location, Date Posted, Job Type, and Experience Level fields
- Filtering job results via minimum years of experience mentioned in job description snippets
- Filtering job results via keywords in job titles
- Scraping all pages returned
- Scraping a specific number of pages
- Custom minimum crawl delay (time between page requests are randomized between the minimum specified and 1.5x the specified amt.)
- Duplicate result handling (only unique results are appended to resulting Excel spreadsheet)
- Job tracking (Scraper will not overwrite the 'Applied' status of a job record in the Excel spreadsheet if it encounters the same job in a future scrape)

## Disclaimer

This project is intended for educational purposes only. The software is provided "as is" without warranty of any kind, express or implied. The developers of this project do not endorse or encourage any activities that may violate the robots.txt file, Terms of Service, or any other usage policies of websites being scraped.

Users of this software are responsible for ensuring that their use of the software complies with all applicable laws and website policies. The developers of this project will not be liable for any damages or legal consequences resulting from the use of this software.

Please use this software responsibly and ethically.
