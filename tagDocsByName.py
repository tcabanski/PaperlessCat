import requests
from collections import namedtuple
import logging
import pathlib
from tags import tags_to_assign
from tags import validate_tags
from correspondent import choose_correspondent

log = logging.getLogger("global")
console = logging.StreamHandler()
formatter =  logging.Formatter('%(asctime)s %(levelname)s : %(message)s')
console.setFormatter(formatter)
log.addHandler(console)
log.setLevel(logging.INFO)
log.info("Starting")

#config
map_document_type_id = 1
pdf_document_type_id = 13
max_docs_to_process = 999000
only_process_empty_doc_type = True
AUTH_CREDENTIALS = ("tom", "paperless")

validate_tags(AUTH_CREDENTIALS)
selected_correspondent = choose_correspondent(AUTH_CREDENTIALS)

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
log.info(f"Processing {docs_to_process} documents")

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

        #assign tags to pages for later update
        tags_to_assign_set = {(tag["name"].lower(), frozenset(tag["excludeWords"]), tag["id"], frozenset(tag["synonyms"])) for tag in tags_to_assign}
        title_lower = title.lower()
       
        for tag_name, exclude_words, tag_id, synonyms in tags_to_assign_set:
           if tag_name in title_lower and not any(exclude_word in title_lower for exclude_word in exclude_words):
               pages_to_update.setdefault(docId, []).append(tag_id)
           elif any(synonym in title_lower and not any(exclude_word in title_lower for exclude_word in exclude_words) for synonym in synonyms):
               pages_to_update.setdefault(docId, []).append(tag_id)

        docs += 1
        if docs == max_docs_to_process:
            break
    #end for
        
    page_url = raw_json["next"]
    log.info(f"processed {docs} of {docs_to_process} documents")
#end while
               
log.info(f"Processing complete. Bulk update being prepared for {docs} documents")

#build dictionary keyed by tag where each tag has the list of pages for the tag
pages_by_tags = {}
for key, tags in pages_to_update.items():
    for tag_to_assign in tags:
        if tag_to_assign:
            pages_by_tags.setdefault(tag_to_assign, []).append(key)
#end for

#Call bulk edit on each tag to update pages with tag
for key in pages_by_tags.keys():
    log.info(f"Bulk updating pages for tag {key} with documents {pages_by_tags[key]}")
    
    body = {
        "documents": pages_by_tags[key],
        "method": "modify_tags",
        "parameters": {
            "add_tags": [ key ],
            "remove_tags": []
        }
    }
    edit_response = requests.post("http://localhost:8000/api/documents/bulk_edit/", auth = AUTH_CREDENTIALS, json = body)
    log.debug(edit_response)

    if edit_response.status_code != 200:
        log.error(f"Failed to bulk edit for tag {key}.  Error is {edit_response.reason}")
#end for
        
#call bulk edit for the correspondent
if int(selected_correspondent) != 0:
    log.info(f"Bulk updating {len(all_documents)} documents for correspondent with id {selected_correspondent}. Documents: {all_documents}")

    body = {
        "documents": all_documents,
        "method": "set_correspondent",
        "parameters": {
            "correspondent": int(selected_correspondent)
        }
    }
    edit_response = requests.post("http://localhost:8000/api/documents/bulk_edit/", auth = AUTH_CREDENTIALS, json = body)
    log.debug(edit_response)

    if edit_response.status_code != 200:
        log.error(f"Failed to bulk edit for correspondent with id {selected_correspondent}.  Error is {edit_response.reason}")
#end if

#call bulk edit for the map document type
log.info(f"Bulk updating {len(map_documents)} documents for map document type with id {map_document_type_id}. Documents: {map_documents}")

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
log.info(f"Bulk updating {len(pdf_documents)} documents for uncategorized document type with id {pdf_document_type_id}. Documents: {pdf_documents}")

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
