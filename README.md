# Job Listing Scraper

This application scrapes Indeed job results and parses the data into a working CSV file that users can use for their job search.

## Usage

![Screenshot of Feature X](./screenshots/gui.png)

Coming Soon. Installation and usage steps to run the application will be provided in a further update.

## Features

- User-friendly GUI via customTkinter
- Searching jobs using Position, Location, Date Posted, Job Type, and Experience Level fields
- Filtering job results via the years of experience mentioned in job descriptions
- Filtering job results via keywords in job titles
- Scraping all pages returned
- Scraping a specific number of pages
- Duplicate result handling (only unique results are appended to resulting CSV)
- Job tracking (Scraper will not overwrite the 'Applied' status of a job record in the CSV if it encounters the same job in a future scrape)
