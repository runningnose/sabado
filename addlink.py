#!/usr/local/bin/python3

import json
import shutil
import os
from datetime import datetime, timedelta

WEB_DIR = os.environ['WEB_DIR']
HOME = os.environ['HOME']

def get_previous_day(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    previous_day = date_obj - timedelta(days=1)
    return previous_day.strftime('%Y-%m-%d')

def get_next_day(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    next_day = date_obj + timedelta(days=1)
    #if next_day > datetime.today():
    #    return None
    return next_day.strftime('%Y-%m-%d')

def find_oldest_links_json():
    oldest_date = None
    oldest_file = None
    
    # Loop through each file in the directory
    for filename in os.listdir(f'{HOME}/sabado'):
    #for filename in os.listdir(f'/tmp'):
        if filename.startswith('links_') and filename.endswith('.json'):
            # Extract the date part from the filename
            date_str = filename[6:-5]  # Remove the 'links_' prefix and '.json' suffix
            try:
                # Convert the date string to a datetime object
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                # Check if this file's date is older or if it's the first file being checked
                if oldest_date is None or file_date < oldest_date:
                    oldest_date = file_date
                    oldest_file = filename
            except ValueError:
                print(f"Skipping invalid date format in file name: {filename}")
    
    # Print the oldest file
    if oldest_file:
        oldest_file = f'{HOME}/sabado/' + oldest_file
        #oldest_file = '/tmp/' + oldest_file
        print(f"The oldest file is: {oldest_file}")
        return (oldest_file, oldest_date.date())
    else:
        print("No valid dated files found.")
        return (None, None)

# Function to read JSON data from a file
def read_json_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.load(file)

def contains_financial_news_source(text):
    return True
    financial_news_sources = ['bloomberg', 'wsj', 'nytimes', 'cnbc', 'barron']
    for source in financial_news_sources:
        if source.lower() in text.lower():
            return True
    return False

# Function to generate HTML with embedded CSS from the JSON data
def generate_html(data):
    html_content = '''
<html>
<head>
    <meta charset="UTF-8">
    <title>URLs by Date</title>

    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333366; }
        h2 { color: #666699; }
        ul { list-style-type: none; padding: 0; }
        li { margin: 10px 0; }
        a { text-decoration: none; color: #0066cc; }
        a:hover { text-decoration: underline; }
        img {
            display: block;
            margin: auto;
            /* Set width to 8.8% of its original size to achieve a smaller scale */
            width: 8.8%;
            height: auto;
        }
    </style>

    <script>
        // Function to hide the link and open it in a new tab
        function hideAndOpenLink(event) {
            // Prevent the default link action
            event.preventDefault();
            // Hide the clicked link
            event.target.style.display = 'none';
            // Open the link in a new tab
            window.open(event.target.href, '_blank');
        }
    </script>
</head>
<body>
<a href="http://www.choo-choo-train.com"><img src="choo-choo-train.webp" alt="Choo Choo Train"></a>
'''
    
    for date, urls in data.items():
        html_content += f'<h2>{date}</h2>\n<ul>\n'
        for url in urls:
            ulist = eval(url)
            if contains_financial_news_source(ulist[0]): 
                html_content += f'<li><a href="{ulist[0]}"  onclick="hideAndOpenLink(event)">{ulist[0]}</a>  [ {ulist[1]} ] <a href="http://www.RemovePaywall.com/{ulist[0]}" target="_blank">RemovedPaywall</a></li>\n'
        
        prev_date = get_previous_day(date)
        html_content += f'<li><a href="{prev_date}.html">http://www.choo-choo-train.com/{prev_date}.html</a></li>'

        next_date = get_next_day(date)
        if next_date:
           html_content += f'<li><a href="{next_date}.html">http://www.choo-choo-train.com/{next_date}.html</a></li>'
        html_content += '</ul>\n'

    html_content += '</body>\n</html>'
    return html_content

# Function to save HTML content to a file
def save_html(filename, content):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

# Main function to process the JSON file and generate HTML
def main(json_filename, old_date):
    # Read JSON from file
    data = read_json_file(json_filename)
    
    print(data)

    # Generate HTML content from JSON data
    html_content = generate_html(data)
    
    os.rename(json_filename, f'{WEB_DIR}/data/links_{old_date}.json')

    html_filename = f'{WEB_DIR}/{old_date}.html'
    
    # Save the generated HTML to a file
    save_html(html_filename, html_content)

    os.unlink(f'{WEB_DIR}/index.html')
    os.symlink(html_filename, f'{WEB_DIR}/index.html')
    shutil.copy(html_filename, f'{WEB_DIR}/data/{old_date}.html')

# Example usage
if __name__ == '__main__':
    (json_filename, old_date) = find_oldest_links_json()  # Change to the path of your JSON file
    print(old_date)
    if json_filename:
        main(json_filename, old_date)
    else:
        print('No json file to process')

