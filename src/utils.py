import datetime
import json
import os
import csv
import hashlib

def build_indeed_url(position, location, experience_level, job_type, max_days_posted_ago):            
    template = 'https://www.indeed.com/jobs?q={}&l={}&sc={}jt{}%3B&fromage={}'
    url = template.format(position, location, experience_level, job_type, max_days_posted_ago)

    return url

def exclude_based_on_title(excluded_keywords, title) -> bool:
    title_split = title.split()
    n = len(title_split)

    for idx, word in enumerate(title_split):
        if (
            word.lower() in excluded_keywords or 
            (idx < n-1 and (word + ' ' + title_split[idx+1]).lower() in excluded_keywords)
        ):
            return True
        
    return False

def get_next_page_url(url):
    # Locate 'start' tag in the URL
    html_param_length = len("&start=")
    tag_start_idx = 0
    tag_end_idx = html_param_length

    while tag_end_idx < len(url):
        if url[tag_start_idx:tag_end_idx] == "&start=":
            break
        tag_start_idx += 1
        tag_end_idx += 1

    if tag_end_idx == len(url):
        return url + "&start=10"
    else:
        # Locate last digit of the start tag
        digit_start_idx = tag_end_idx
        digit_end_idx = tag_end_idx
        
        while digit_end_idx < len(url) and url[digit_end_idx].isdigit():
            digit_end_idx += 1
        
        curr_start_num = int(url[digit_start_idx:digit_end_idx])

        return url[:tag_end_idx] + str(curr_start_num + 10) + url[digit_end_idx:]

def read_jobs_csv(filename):
    data = {} # hash_id : record
    file_exists = os.path.isfile(filename)

    if not file_exists: 
        return data

    with open(filename, 'r') as csv_file:
        # Create a DictReader object
        csv_reader = csv.DictReader(csv_file)

        # Iterate over each row in the csv file
        for row in csv_reader:
            data[row['hash_id']] = row
    
    return data

# Updates all records in the CSV to respect new header structure
def update_jobs_csv_headers(filename, new_headers):
    # Read the existing CSV data
    with open(filename, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        existing_data = list(reader)
    
    # Update the data with empty values for the new headers
    updated_data = []
    for row in existing_data:
        updated_row = {header: row.get(header, '') for header in new_headers}
        updated_data.append(updated_row)

    # Overwrite the CSV with the updated data
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=new_headers)
        writer.writeheader()
        writer.writerows(updated_data)
    
    return

def write_jobs_csv(filename, job_records):
    with open('config.json') as config_file:
        config = json.load(config_file)

    # Check if the file exists and is non-empty
    file_exists = os.path.isfile(filename) and os.path.getsize(filename) > 0
    fieldnames = config['csv_headers']

    with open(filename, "w", newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, dialect='excel')
        
        # Update the header structure for all records if the order or type of attributes have changed
        if file_exists:
            with open(filename, 'r', newline='') as read_file:
                reader = csv.reader(read_file)
                existing_headers = next(reader, None)

                if existing_headers and set(existing_headers) != set(fieldnames):
                    update_jobs_csv_headers(filename, new_headers=fieldnames)

        # Write the new data
        writer.writeheader()
                    
        for job_record in job_records.values():
            writer.writerow(job_record)
    
    return

def string_to_hash(input_string):
    # Encode the string to bytes
    encoded_string = input_string.encode()

    # Create a SHA-256 hash object
    hash_object = hashlib.sha256(encoded_string)

    # Get the hexadecimal representation of the hash
    hex_hash = hash_object.hexdigest()

    return hex_hash

def parse_indeed_url(url):
    count = 0

    for idx, char in enumerate(url):
        if char == '=':
            count += 1
            if count == 2:
                return url[:idx]
    return url

def parse_post_date(post_date_string):
    split_post_date = post_date_string.split()

    # Case: Posted today
    if post_date_string == "Today" or post_date_string == "Just posted" or split_post_date[0] == "Visited":
        return datetime.date.today().strftime("%m/%d/%y")

    try:
        num_days_ago = int(split_post_date[1])

        today = datetime.date.today()
        posted_date = today - datetime.timedelta(days=num_days_ago)
        return posted_date.strftime("%m/%d/%y")

    except:
        return datetime.date.today().strftime("%m/%d/%y")