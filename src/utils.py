import re
import datetime
import json
import os
import csv
import hashlib
from functools import reduce

def build_indeed_url(position, location, experience_level, job_type, max_days_posted_ago):            
    template = 'https://www.indeed.com/jobs?{}'
    formatted_params = []

    # Format the URL parameters into proper HTML parameters
    if position:
        formatted_params.append("q=" + position)
    if location:
        formatted_params.append("&l=" + location)

    if experience_level and job_type:
        formatted_params.append("&sc=0kf%3Aexplvl" + experience_level + "jt" + job_type + "%3B")
    elif experience_level:
        formatted_params.append("&sc=0kf%3Aexplvl" + experience_level + "%3B")
    elif job_type:
        formatted_params.append("&sc=0kf%3Ajt" + job_type + "%3B")
    
    if max_days_posted_ago:
        formatted_params.append("&fromage=" + max_days_posted_ago)

    url = template.format(''.join(formatted_params))

    return url

def exclude_based_on_title(excluded_keywords, cleaned_title) -> bool:
    cleaned_title = re.sub(r'[^a-zA-Z0-9]', ' ', cleaned_title)
    title_split = cleaned_title.split()
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
    print("Updating CSV headers")
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
    
    print("Done updating CSV headers")
    return

def write_jobs_csv(filename, job_records):
    print("Updating CSV record data")
    with open('config.json') as config_file:
        config = json.load(config_file)

    # Check if the file exists and is non-empty
    file_exists = os.path.isfile(filename) and os.path.getsize(filename) > 0
    fieldnames = config['csv_settings']['csv_headers']

    with open(filename, "w", newline='', errors='replace') as csv_file:
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
    print("Done updating CSV records")
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
        num_days_ago = int(split_post_date[2])

        today = datetime.date.today()
        posted_date = today - datetime.timedelta(days=num_days_ago)
        return posted_date.strftime("%m/%d/%y")

    except:
        return datetime.date.today().strftime("%m/%d/%y")

# Checks if the indeed link is valid based on the prefix of the URL.
def is_valid_indeed_job_link(url):
    # In rare cases, a job card may return 'https://www.indeed.com/pagead/clk?mo=r&ad', which isn't a valid link
    valid_prefix = 'https://www.indeed.com/rc/clk?jk='
    n = len(valid_prefix)

    if url[:n] == valid_prefix:
        return True
    return False

def is_valid_description_criteria(description):
    # Regular expression to match variations of years of experience
    regex = r'(\d+)\+?[\s\w]* years'
    matches = re.findall(regex, description, re.IGNORECASE)

    if matches:
        years = list(map(int, matches))
        min_exp = min(years)

        with open('config.json') as config_file:
            config = json.load(config_file)

        user_years_of_experience = (config['indeed_criteria'])['user_years_of_experience']
        if int(user_years_of_experience) < min_exp:
            return False
        else:
            return True
    else:
        return True
    
def update_config_field(filepath, field_path, new_value):
    if field_path == 'excluded_keywords':
        # Filter out empty strings from the list of new values
        new_value = sorted([value.lower() for value in new_value if value.strip()])

    # Read the existing config file
    with open(filepath, 'r') as file:
        config = json.load(file)

    # Split the field path into a list of keys
    keys = field_path.split('.')

    # Update the field value
    reduce(lambda d, k: d.setdefault(k, {}), keys[:-1], config)[keys[-1]] = new_value

    # Write the updated config back to the file
    with open(filepath, 'w') as file:
        json.dump(config, file, indent=4)