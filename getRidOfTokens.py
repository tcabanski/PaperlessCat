import requests
from collections import namedtuple
import logging
from credentials import get_credentials

log = logging.getLogger("global")
console = logging.StreamHandler()
formatter =  logging.Formatter('%(asctime)s %(levelname)s : %(message)s')
console.setFormatter(formatter)
log.addHandler(console)
log.setLevel(logging.INFO)
log.debug("Starting")

#config
auth_credentials = get_credentials()
mapDocumentTypeId = 1
pdfDocumentTypeId = 13
maxDocsToProcess = 999000
onlyProcessEmptyDocType = True

# Scan through tokens and art and delete everything past the first 2500 docs
docs = 0
pageUrl = "http://jittikun:8000/api/documents/?document_type__id__in=14&sort=created&reverse=1"

docsToDelete = []

response = requests.get(pageUrl, auth = auth_credentials)
rawJson = response.json()
log.debug(rawJson)

docsToProcess = len(rawJson["all"])

log.debug(f"Processing {docsToProcess} documents")
for docId in rawJson["all"]:
    log.debug(f"process docId {docId}")
    if docs > 2500:
        docsToDelete.append(docId)
    #end if

    docs += 1
    if docs == maxDocsToProcess:
        break
#end for
        
body = {
        "documents": docsToDelete,
        "method": "delete",
        "parameters": {
        }
    }

log.debug(f"Bulk deleting {len(docsToDelete)} documents. Documents: {docsToDelete}")
               
editResponse = requests.post("http://jittikun:8000/api/documents/bulk_edit/", auth = auth_credentials, json = body)
log.debug(editResponse)

if editResponse.status_code != 200:
    log.error(f"Failed to bulk delete pages.  Full response is {editResponse}")
