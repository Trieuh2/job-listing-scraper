import re
import datetime
import json
import os
import hashlib
from functools import reduce
from typing import List, Dict, Union, cast

from openpyxl import Workbook, load_workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.formatting.formatting import ConditionalFormattingList
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet

def build_indeed_url(position: str, location: str, experience_level: str, job_type: str, max_days_posted_ago: str) -> str:
    """Builds a URL for Indeed job search based on the given parameters."""
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

def exclude_based_on_title(excluded_keywords: List[str], cleaned_title: str) -> bool:
    """Returns True if the cleaned title contains any excluded keywords."""
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

def get_next_page_url(url: str) -> str:
    """Returns the URL for the next page of job listings."""
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

def read_jobs_excel(filename: str) -> Dict[str, Dict[str, Union[str, int, float]]]:
    """Reads job records from an Excel file and returns a dictionary of data."""
    data = {}  # hash_id : record
    file_exists = os.path.isfile(filename)

    if not file_exists:
        return data

    # Load the workbook and get the active sheet
    wb = load_workbook(filename)
    ws = cast(Worksheet, wb.active)

    # Get the headers from the first row
    headers = [cell for cell in next(ws.iter_rows(min_row=1, max_row=1, values_only=True))]

    # Iterate over each row in the Excel sheet
    for row in ws.iter_rows(min_row=2, values_only=True):
        record = dict(zip(headers, row))
        data[record['hash_id']] = record

    return data


def update_jobs_excel_headers(filename: str, new_headers: List[str]) -> None:
    """Updates the headers of the Excel file with the new headers."""
    print("Updating Excel headers")

    # Check if the file exists
    file_exists = os.path.isfile(filename)
    if not file_exists:
        print(f"File {filename} does not exist.")
        return

    # Load the workbook and get the active sheet
    wb = load_workbook(filename)
    ws = cast(Worksheet, wb.active)

    # Read the existing data
    existing_data = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        existing_data.append(row)

    # Clear the sheet
    ws.delete_rows(1, ws.max_row)

    # Write the new headers
    ws.append(new_headers)

    # Update the data with empty values for the new headers
    updated_data = []
    for row in existing_data:
        updated_row = {header: '' for header in new_headers}
        for i, cell in enumerate(row):
            header = ws.cell(row=1, column=i + 1).value
            if header in updated_row:
                updated_row[header] = cell
        updated_data.append(list(updated_row.values()))

    # Write the updated data
    for row in updated_data:
        ws.append(row)

    # Save the workbook
    wb.save(filename)

    print("Done updating Excel headers")


def write_jobs_excel(filename: str, job_records: Dict[str, Dict]) -> None:
    """Writes job records to an Excel file."""
    print("Updating Excel record data")

    with open('config.json') as config_file:
        config = json.load(config_file)

    # Check if the file exists
    file_exists = os.path.isfile(filename)
    fieldnames = config['csv_settings']['csv_headers']

    # Create a new workbook or load the existing one
    if file_exists:
        wb = load_workbook(filename)
        ws = cast(Worksheet, wb.active)
    else:
        wb = Workbook()
        ws = cast(Worksheet, wb.active)
        # Write the headers in the new file
        ws.append(fieldnames)

    # Clear existing data if the file already exists
    if file_exists:
        for row in ws.iter_rows(min_row=2, max_col=len(fieldnames), max_row=ws.max_row):
            for cell in row:
                cell.value = None

    # Sort the job records first by 'posted_date' in reverse, then by 'company' in normal order
    sorted_job_records = sorted(job_records.values(), key=lambda x: x.get('company', ''))
    sorted_job_records.sort(key=lambda x: x['posted_date'], reverse=True)

    # Write the new data starting from row 2
    row_num = 2
    for job_record in sorted_job_records:
        col_num = 1
        for header in fieldnames:
            cell = ws.cell(row=row_num, column=col_num, value=job_record.get(header, ''))

            if header == 'job_link' and cell.value:  # Check if the column is 'job_link' and has a value
                setattr(cell, "hyperlink", cell.value) # Set the hyperlink
                cell.style = 'Hyperlink'  # Apply the hyperlink style
            col_num += 1
        row_num += 1

    # Remove existing conditional formatting rules for the worksheet
    ws.conditional_formatting = ConditionalFormattingList()

    # Apply conditional formatting to the 'applied' column
    green_fill = PatternFill(start_color='CCFFCC', end_color='CCFFCC', fill_type='solid')
    red_fill = PatternFill(start_color='FFCCCC', end_color='FFCCCC', fill_type='solid')
    yellow_fill = PatternFill(start_color='FFFF99', end_color='FFFF99', fill_type='solid')
    ws.conditional_formatting.add('B2:B{}'.format(ws.max_row), CellIsRule(operator='equal', formula=['"Yes"'], fill=green_fill))
    ws.conditional_formatting.add('B2:B{}'.format(ws.max_row), CellIsRule(operator='equal', formula=['"No"'], fill=red_fill))
    ws.conditional_formatting.add('B2:B{}'.format(ws.max_row), CellIsRule(operator='equal', formula=['"Skip"'], fill=yellow_fill))

    # Update or create the table with starting from row 2
    table_exists = len(ws.tables) > 0
    if table_exists:
        table = ws.tables[next(iter(ws.tables))]
        table.ref = f"A1:{chr(64 + len(fieldnames))}{ws.max_row}"
        table.tableStyleInfo.showRowStripes = True 
    else:
        table = Table(displayName="JobTable", ref=f"A1:{chr(64 + len(fieldnames))}{ws.max_row}")
        style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                               showLastColumn=False, showRowStripes=True, showColumnStripes=False)
        table.tableStyleInfo = style
        ws.add_table(table)

    # Save the workbook
    wb.save(filename)
    print("Done updating Excel records")

def string_to_hash(input_string: str) -> str:
    """Converts a string to a SHA-256 hash."""
    # Encode the string to bytes
    encoded_string = input_string.encode()

    # Create a SHA-256 hash object
    hash_object = hashlib.sha256(encoded_string)

    # Get the hexadecimal representation of the hash
    hex_hash = hash_object.hexdigest()

    return hex_hash

def parse_indeed_url(url: str) -> str:
    """Parses an Indeed URL and returns the base URL."""
    count = 0

    for idx, char in enumerate(url):
        if char == '=':
            count += 1
            if count == 2:
                return url[:idx]
    return url

def parse_post_date(post_date_string: str) -> str:
    """Parses a post date string and returns the formatted date."""
    split_post_date = post_date_string.split()

    # Case: Posted today
    if post_date_string == "Today" or post_date_string == "Just posted" or split_post_date[0] == "Visited":
        return datetime.date.today().strftime("%m/%d/%Y")

    try:
        num_days_ago = int(split_post_date[2])

        today = datetime.date.today()
        posted_date = today - datetime.timedelta(days=num_days_ago)
        return posted_date.strftime("%m/%d/%Y")

    except:
        return datetime.date.today().strftime("%m/%d/%Y")

# Checks if the indeed link is valid based on the prefix of the URL.
def is_valid_indeed_job_link(url: str) -> bool:
    """Checks if an Indeed job link is valid."""
    # In rare cases, a job card may return 'https://www.indeed.com/pagead/clk?mo=r&ad', which isn't a valid link
    valid_prefix = 'https://www.indeed.com/rc/clk?jk='
    n = len(valid_prefix)

    if url[:n] == valid_prefix:
        return True
    return False

def is_valid_description_criteria(description: str) -> bool:
    """Checks if a job description meets the specified years of experience criteria."""
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
    
def update_config_field(filepath: str, field_path: str, new_value) -> None:
    """Updates a specific field in the config.json configuration file."""
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

def is_valid_numerical_field_input(input: str) -> bool:
    """Checks if an input string is a valid numerical field."""
    return input.isdigit() or input== ""