import requests
import re
from collections import namedtuple
import logging
import pathlib
from document import Document

log = logging.getLogger("global")
console = logging.StreamHandler()
formatter =  logging.Formatter('%(asctime)s %(levelname)s : %(message)s')
console.setFormatter(formatter)
log.addHandler(console)
log.setLevel(logging.INFO)
log.info("Starting")

#config
map_document_type_id = 1
grid_tag_id = 34
AUTH_CREDENTIALS = ("tom", "paperless")

# Scan through all the documents and find gridded duplicates
docs = 0
page_url = "http://localhost:8000/api/documents/?document_type=1"


map_documents = []
with_grid = []
response = requests.get(page_url, auth = AUTH_CREDENTIALS)
raw_json = response.json()
log.debug(raw_json)

doc_count = len(raw_json["all"])
log.info(f"Processing {doc_count} documents")

page_url = "http://localhost:8000/api/documents/?document_type=1&page_size=10000"
while page_url is not None:
    response = requests.get(page_url, auth = AUTH_CREDENTIALS)
    raw_json = response.json()
    log.debug(raw_json)

    for doc_result in raw_json["results"]:
        doc = Document(doc_result["id"], doc_result["title"].lower(), doc_result["original_file_name"].lower(), 
                       grid_tag_id in doc_result["tags"])
        map_documents.append(doc)
        if (doc.has_grid_tag):
            with_grid.append(doc)
        #end if
        
        docs += 1
    #end for
        
    page_url = raw_json["next"]
    log.info(f"processed {docs} of {doc_count} documents")
#end while
log.info(f"processed {docs} of {doc_count} documents and found {len(with_grid)} with grid")
