import os
import requests
import logging
from credentials import get_credentials

log = logging.getLogger("global")
console = logging.StreamHandler()
formatter =  logging.Formatter('%(asctime)s %(levelname)s : %(message)s')
console.setFormatter(formatter)
log.addHandler(console)
log.setLevel(logging.INFO)
log.info("Starting")
maxDocs = 0

#config
auth_credentials = get_credentials()

# Set your Paperless-ngx API base URL and API token
API_URL = "http://jittikun:8000/api/documents/?sort=added&page-size=100"
DOWNLOAD_DIR = "C:\\Users\\tom\\Downloads"

# Function to download a document
def download_document(document_id, original_name, download_url):
    response = requests.get(download_url, auth = auth_credentials)
    if response.status_code == 200:
        file_path = os.path.join(DOWNLOAD_DIR, original_name)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        log.debug(f"Downloaded: {original_name}")
    else:
        log.error(f"Failed to download document {original_name}. Status code: {response.status_code}")

# Function to fetch documents with pagination
def fetch_and_download_documents(url):
    docCount = 0
    while url and (docCount < maxDocs or maxDocs == 0):
        response = requests.get(url, auth = auth_credentials)
        if response.status_code == 200:
            data = response.json()
            documents = data.get('results', [])
            for document in documents:
                docCount += 1
                document_id = document['id']
                original_name = document['original_file_name']
                download_url = f"http://jittikun:8000/api/documents/{document_id}/download/?original=true"
                
                # Download the document with its original file name
                download_document(document_id, original_name, download_url)

            # Check for the next page
            log.info(f"processed {docCount} documents")
            url = data.get('next')
        else:
            log.error(f"Failed to fetch documents. Status code: {response.status_code}")
            break

    log.info(f"processed {docCount} documents")

# Start fetching and downloading documents
fetch_and_download_documents(API_URL)
