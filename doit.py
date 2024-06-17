import sys
import os
import base64
import json
import requests
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from urllib.parse import urlparse
from openai import OpenAI
from PIL import Image
from PIL.ExifTags import TAGS
from io import BytesIO

# Constants                                                                                                             
SCOPES = os.environ['SCOPES']                                                     
API_SERVICE_NAME = os.environ['API_SERVICE_NAME']
API_VERSION = os.environ['API_VERSION'] 
REFRESH_TOKEN = os.environ['REFRESH_TOKEN'] 
CLIENT_ID = os.environ['CLIENT_ID'] 
CLIENT_SECRET = os.environ['CLIENT_SECRET'] 
API_KEY = os.environ['API_KEY'] 
SEARCH_ID = os.environ['SEARCH_ID'] 
TODAY = datetime.date.today().strftime('%Y-%m-%d')
#TODAY = '2024-05-20'
TODAY = '2024-06-11'

mlinks = []

def authenticate_google_photos():
    creds = Credentials(None, refresh_token=REFRESH_TOKEN, token_uri='https://oauth2.googleapis.com/token',
                        client_id=CLIENT_ID, client_secret=CLIENT_SECRET, scopes=[SCOPES,])
    return build(API_SERVICE_NAME, API_VERSION, credentials=creds, static_discovery=False)

def get_photos_by_date(service, date):
    """
    Get photos by specific date. Date format: 'YYYY-MM-DD'
    """
    startDate, endDate = date, date
    filters = {                                                                                                                 'dateFilter': {                                                                                                             'ranges': [                                                                                                                 {   
    'startDate': {'year': int(startDate[:4]), 'month': int(startDate[5:7]), 'day': int(startDate[8:10])},
                    'endDate': {'year': int(endDate[:4]), 'month': int(endDate[5:7]), 'day': int(endDate[8:10])}
                }
            ]
        },
    'mediaTypeFilter': {
            'mediaTypes': ['PHOTO']
        }
    }
    request_body = {
        'filters': filters
    }
    photos = service.mediaItems().search(body=request_body).execute()
    print('photos-->')
    print(photos)
    items = photos.get('mediaItems', [])
    return items

def download_photo(photo_url, photo_id, directory):
    response = requests.get(photo_url)

    # Check if the directory exists
    if not os.path.isdir(directory):
        # If the directory does not exist, create it
        os.makedirs(directory)
        print(f"Directory '{directory}' created successfully.")
    else:
        print(f"Directory '{directory}' already exists.")

    if response.status_code == 200:
        with open(f'{directory}/{photo_id}.jpg', 'wb') as file:
            file.write(response.content)
    else:
        print("Failed to download photo.")

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def google_search(search_title):
    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'q': search_title,
        'key': API_KEY,
        'cx': SEARCH_ID
        }

    response = requests.get(url, params=params)
    results = response.json()
    #print(results)
    if 'items' in results:
        return results['items'][0]['link']
    else:
        return 'Not found'

def get_image_txt(filename, client):
    # Encode the image to base64
    base64_image = encode_image(filename)
    
    '''
    response = client.chat.completions.create(
      model="gpt-4-turbo",
      messages=[
            {"role": "user", "content": [
                {"type": "text", "text": "Return JSON document with data. Only return JSON not other text"},   
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ],
      max_tokens=600,
    )
    '''
   
    response = client.chat.completions.create(
      model="gpt-4-turbo",
      messages=[
            {"role": "user", "content": [
                {"type": "text", "text": "find the title of articles shown in the picture, return them as python list not other text, no need to add 'article_titles ='"},   
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ],
      max_tokens=600,
    )

    nl = eval((response.choices[0].message.content).replace("```python\n", "").replace("\n```", ""))

    for l in nl:
        print(l)
        link = google_search(l)
        if link != 'Not found':
            l = l.replace('"','\'')
            l = l.replace("'",' ')
            mlinks.append([link,l])
        print(link)
        print('\n')
    print(mlinks)
    print('----------------------\n')


def get_camera_make(image_path):
    # Open an image file
    with Image.open(image_path) as img:
        # Get EXIF data
        try:
           exif_data = img._getexif()
           # Initialize a dictionary to hold decoded EXIF data
           exif = {}
           if exif_data:
               # Decode EXIF data
               for tag_id, value in exif_data.items():
                   tag = TAGS.get(tag_id, tag_id)
                   exif[tag] = value

               # Return the manufacturer if available
               return exif.get('Make')
        except:
            pass

    return "No EXIF data available"

def check_images(directory, client):
    # Loop through all files in the directory
    for filename in os.listdir(directory):
            # Check if the file is an image file
            if filename.endswith(".jpg") or filename.endswith(".png") or filename.endswith(".jpeg"):
                # Construct the full file path
                file_path = os.path.join(directory, filename)
        
                camera_make = get_camera_make(file_path)
        
                if camera_make != 'Apple' or camera_make == 'No EXIF data available':
                    print(f"Process this screenshot:{filename}, make:{camera_make}")
                    get_image_txt(file_path, client)
                else:
                    print(f"Camera is: -{camera_make}-")
        
# Main code
if __name__ == "__main__":
    service = authenticate_google_photos()
    print(service)
    directory = './data/photos/{}'.format(TODAY)
    photos = get_photos_by_date(service, TODAY)
    for photo in photos:
        download_photo(photo['baseUrl'] + '=d', photo['id'], directory)
    if not photos:
        sys.exit(0)
    client = OpenAI()
    check_images(directory, client)

    with open(f'./links_{TODAY}.json', 'w') as file:
        _str = f'{{\n"{TODAY}":\n'
        file.write(_str)
        _str = '['
        for l in mlinks:
           _str += f'\"{l}\",\n'
        _str = _str[:-2]
        _str += ']\n}\n'
        file.write(_str)

