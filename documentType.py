import requests
import logging

def bulk_edit_document_type(documents, document_type_id, auth_credentials):
    log = logging.getLogger("global")
    log.debug(f"Bulk updating {len(documents)} documents for map document type with id {document_type_id}. Documents: {documents}")

    body = {
        "documents": documents,
        "method": "set_document_type",
        "parameters": {
            "document_type": document_type_id
        }
    }
    edit_response = requests.post("http://jittikun:8000/api/documents/bulk_edit/", auth = auth_credentials, json = body)
    log.debug(edit_response)

    if edit_response.status_code != 200:
        log.error(f"Failed to bulk edit for map document type with id {document_type_id}.  Error is {edit_response.reason}")