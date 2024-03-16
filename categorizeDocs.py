import requests
from collections import namedtuple
import logging
import json

log = logging.getLogger("global")
console = logging.StreamHandler()
formatter =  logging.Formatter('%(asctime)s %(levelname)s : %(message)s')
console.setFormatter(formatter)
log.addHandler(console)
log.setLevel(logging.INFO)
log.info("Starting")

#config
AUTH_CREDENTIALS = ("tom", "paperless")
map_document_type_id = 1
pdf_document_type_id = 13

with open("MapDocuments.json") as map_documents_file:
    map_documents = json.load(map_documents_file)

with open("PdfDocuments.json") as pdf_documents_file:
    pdf_documents = json.load(pdf_documents_file)


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