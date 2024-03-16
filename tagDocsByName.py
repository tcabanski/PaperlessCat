import requests
from collections import namedtuple
import logging
import pathlib
from tags import tags_to_assign
from tags import validate_tags
from correspondent import choose_correspondent
import json

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

        for tag_to_assign in tags_to_assign:
            #Tag if the title includes the name of the tag and one of the exclude words is not present
            if title.lower().find(tag_to_assign["name"].lower()) > -1:
                excluded = False
                for excludeWord in tag_to_assign["excludeWords"]:
                    if title.lower().find(excludeWord.lower()) > -1:
                        excluded = True
                        break;
                #end for
                
                if not excluded:
                    if docId in pages_to_update:
                        if tag_to_assign["id"] not in pages_to_update[docId]:
                            pages_to_update[docId].append(tag_to_assign["id"])
                    else:
                        pages_to_update[docId] = [tag_to_assign["id"]]
                    #end if
                #end if
            #end if

            #Tag if the title includes one of the synomnyms and not one of the exluded words
            for synonym in tag_to_assign["synonyms"]:
                if title.lower().find(synonym.lower()) > -1:
                    excluded = False
                    for excludeWord in tag_to_assign["excludeWords"]:
                        if title.lower().find(excludeWord.lower()) > -1:
                            excluded = True
                            break;
                    #end for

                    if docId in pages_to_update:
                        if tag_to_assign["id"] not in pages_to_update[docId]:
                            pages_to_update[docId].append(tag_to_assign["id"])
                    else:
                        pages_to_update[docId] = [tag_to_assign["id"]]
            #end for
        #end for

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

with open("MapDocuments.json", "w", encoding="utf-8") as f:
    json.dump(map_documents, f, ensure_ascii=False, indent=4)

with open("PdfDocuments.json", "w", encoding="utf-8") as f:
    json.dump(pdf_documents, f, ensure_ascii=False, indent=4)
