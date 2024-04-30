import json
import shutil
import os
from datetime import datetime, timedelta

WEB_DIR = os.environ['WEB_DIR']

def file_created_yesterday_or_earlier(file_path):
    """
    Checks if a file was created yesterday.
    
    Args:
        file_path (str): The path to the file.
        
    Returns:
        bool: True if the file was created yesterday, False otherwise.
    """
    try:
        # Get the creation time of the file
        creation_time = os.path.getctime(file_path)
        
        # Convert the creation time to a datetime object
        creation_datetime = datetime.fromtimestamp(creation_time)
        
        # Calculate the date of yesterday
        yesterday = datetime.now() - timedelta(days=1)
        
        # Check if the file was created yesterday
        return creation_datetime.date() <= yesterday.date()
    
    except (OSError, ValueError):
        # If there's an error accessing the file, return False
        return False

# Function to read JSON data from a file
def read_json_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def contains_financial_news_source(text):
    return True
    financial_news_sources = ['bloomberg', 'wsj', 'nytimes', 'cnbc', 'barron']
    for source in financial_news_sources:
        if source.lower() in text.lower():
            return True
    return False

# Function to generate HTML with embedded CSS from the JSON data
def generate_html(data, prev_link):
    html_content = '''
<html>
<head>
    <title>URLs by Date</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333366; }
        h2 { color: #666699; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 10px 0; }
        a { text-decoration: none; color: #0066cc; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>URLs Grouped by Date</h1>
'''
    for date, urls in data.items():
        html_content += f'<h2>{date}</h2>\n<ul>\n'
        for url in urls:
            ulist = eval(url)
            if contains_financial_news_source(ulist[0]): 
                html_content += f'<li><a href="{ulist[0]}">{ulist[0]}</a>  [ {ulist[1]} ]</li>\n'
        
        html_content += f'<li><a href="{prev_link}">{prev_link}</a></li>\n'
        html_content += '</ul>\n'
    html_content += '</body>\n</html>'
    return html_content

# Function to save HTML content to a file
def save_html(filename, content):
    with open(filename, 'w') as file:
        file.write(content)

# Main function to process the JSON file and generate HTML
def main(json_filename):
    # Read JSON from file
    data = read_json_file(json_filename)
    
    print(data)
    # Generate the HTML file name based on the current date
    yesterday_date = (datetime.today()-timedelta(days=1)).strftime('%Y_%m_%d')
    prev_json =  f'{WEB_DIR}/data/links_{yesterday_date}.json'
    prev_file = f'{WEB_DIR}/data/links_{yesterday_date}.html'
    prev_link = f'http://www.choo-choo-train.com/data/links_{yesterday_date}.html'

    # Generate HTML content from JSON data
    html_content = generate_html(data, prev_link)
    
    # check if the file: links.html was created yesterday or earlier 
    if file_created_yesterday_or_earlier('{WEB_DIR}/links.html'):
        os.rename('{WEB_DIR}/links.html', prev_file)

    if file_created_yesterday_or_earlier('./links.json'):
        shutil.copy('./links.json', prev_json)

    html_filename = f'{WEB_DIR}/links.html'
    
    # Save the generated HTML to a file
    save_html(html_filename, html_content)

# Example usage
if __name__ == '__main__':
    json_filename = './links.json'  # Change to the path of your JSON file
    main(json_filename)

