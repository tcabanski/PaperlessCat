import requests
from collections import namedtuple
import logging
import pathlib

log = logging.getLogger("global")
console = logging.StreamHandler()
formatter =  logging.Formatter('%(asctime)s %(levelname)s : %(message)s')
console.setFormatter(formatter)
log.addHandler(console)
log.setLevel(logging.INFO)
log.debug("Starting")

#config
AUTH_CREDENTIALS = ("tom", "paperless")
map_document_type_id = 1
pdf_document_type_id = 13
only_process_empty_doc_type = True

# Scan through all the documents and assign likely tags as well as assiging the map document type to things that are not PDF
docs = 0
if only_process_empty_doc_type:
    page_url = "http://localhost:8000/api/documents/?document_type__isnull=1&page_size=100000"
else:
    page_url = "http://localhost:8000/api/documents/?sort=added&page-size=100000"

map_documents = []
pdf_documents = []
all_documents = []
pages_to_update = {}
response = requests.get(page_url, auth = AUTH_CREDENTIALS)
raw_json = response.json()
log.debug(raw_json)

docs_to_process = len(raw_json["all"])
log.debug(f"Collecting {docs_to_process} documents to categorize")

while page_url is not None:
    response = requests.get(page_url, auth = AUTH_CREDENTIALS)
    raw_json = response.json()
    log.debug(raw_json)

    for doc_result in raw_json["results"]:
        docId = doc_result["id"]
        log.debug(f"processing docId {docId}")

        title = doc_result["title"]
        original_file_name = doc_result["original_file_name"]

        all_documents.append(docId)

        if pathlib.Path(original_file_name).suffix.lower() != ".pdf":
            map_documents.append(docId)
        #end if
        
        if pathlib.Path(original_file_name).suffix.lower() == ".pdf":
            pdf_documents.append(docId)
        #end if

        docs += 1
    #end for
        
    page_url = raw_json["next"]
    log.debug(f"processed {docs} of {docs_to_process} documents")
#end while

#call bulk edit for the map document type
log.debug(f"Bulk updating {len(map_documents)} documents for map document type with id {map_document_type_id}. Documents: {map_documents}")

body = {
    "documents": map_documents,
    "method": "set_document_type",
    "parameters": {
        "document_type": map_document_type_id
    }
}
edit_response = requests.post("http://localhost:8000/api/documents/bulk_edit/", auth = AUTH_CREDENTIALS, json = body)
log.debug(edit_response)

if edit_response.status_code != 200:
    log.error(f"Failed to bulk edit for map document type with id {map_document_type_id}.  Error is {edit_response.reason}")

#call bulk edit for the pdf document type
log.debug(f"Bulk updating {len(pdf_documents)} documents for uncategorized document type with id {pdf_document_type_id}. Documents: {pdf_documents}")

body = {
    "documents": pdf_documents,
    "method": "set_document_type",
    "parameters": {
        "document_type": pdf_document_type_id
    }
}
edit_response = requests.post("http://localhost:8000/api/documents/bulk_edit/", auth = AUTH_CREDENTIALS, json = body)
log.debug(edit_response)

if edit_response.status_code != 200:
    log.error(f"Failed to bulk edit for uncategorized document type with id {pdf_document_type_id}.  Error is {edit_response.reason}")

log.info("Categorization done")