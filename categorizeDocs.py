import requests
from collections import namedtuple
import logging
import pathlib
from documentType import bulk_edit_document_type
from credentials import get_credentials
import constants

log = logging.getLogger("global")
console = logging.StreamHandler()
formatter =  logging.Formatter('%(asctime)s %(levelname)s : %(message)s')
console.setFormatter(formatter)
log.addHandler(console)
log.setLevel(logging.INFO)
log.debug("Starting")

#config
auth_credentials = get_credentials()

map_document_type_id = 1
pdf_document_type_id = 13
foundry_map_document_type_id = 17
foundry_module_document_type_id = 15

only_process_empty_doc_type = True

# Scan through all the documents and assign likely tags as well as assiging the map document type to things that are not PDF
docs = 0
if only_process_empty_doc_type:
    page_url = f"http://{constants.API_HOST}:8000/api/documents/?document_type__isnull=1&page_size=100000"
else:
    page_url = f"http://{constants.API_HOST}:8000/api/documents/?sort=added&page-size=100000"

map_documents = []
pdf_documents = []
foundry_modules = []
foundry_maps = [] 
all_documents = []
pages_to_update = {}
response = requests.get(page_url, auth = auth_credentials)
raw_json = response.json()
log.debug(raw_json)

docs_to_process = len(raw_json["all"])
log.debug(f"Collecting {docs_to_process} documents to categorize")

while page_url is not None:
    response = requests.get(page_url, auth = auth_credentials)
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
            if original_file_name.startswith("AnimatedMap_") or original_file_name.startswith("AdventureVTTFile_"):
                foundry_maps.append(docId)
            elif original_file_name.startswith("Module_"):
                foundry_modules.append(docId)
            else:
                pdf_documents.append(docId)
        #end if

        docs += 1
    #end for
        
    page_url = raw_json["next"]
    log.debug(f"processed {docs} of {docs_to_process} documents")
#end while

#call bulk edit for the various document types
bulk_edit_document_type(map_documents, map_document_type_id, auth_credentials)
bulk_edit_document_type(foundry_modules, foundry_module_document_type_id, auth_credentials)
bulk_edit_document_type(foundry_maps, foundry_map_document_type_id, auth_credentials)
bulk_edit_document_type(pdf_documents, pdf_document_type_id, auth_credentials)

log.info("Categorization done")