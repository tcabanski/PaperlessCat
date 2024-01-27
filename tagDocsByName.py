import requests
from collections import namedtuple
import json
import logging
import pathlib

log = logging.getLogger("global")
console = logging.StreamHandler()
formatter =  logging.Formatter('%(asctime)s %(levelname)s : %(message)s')
console.setFormatter(formatter)
log.addHandler(console)
log.setLevel(logging.INFO)
log.info("Starting")

#config
mapDocumentTypeId = 1
maxDocsToProcess = 10000

def tagIdOfName(name, tags, oldId):
    for tag in tags:
        if tag["name"] == name:
            return tag["id"]
        
    return oldId

# Find the ID of key tags
gridTagId = None
nightTagId = None
snowTagId = None
rainTagId = None
fogTagId = None
lavaTagId = None
fireTagId = None
desertTagId = None
astralTagId = None
bloodTagId = None

tagsToAssign = [
    {"name":"Grid", "id": None, "docIds": [], "synonyms": [], "excludeWords": ["No", "Non", "less"]},
    {"name":"Night", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Snow", "id":None, "docIds": [], "synonyms": ["Winter"], "excludeWords": []},
    {"name":"Rain", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Fog", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Lava", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Fire", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Desert", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Astral", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Blood", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Bridge", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Camp", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Castle/Fort/etc.", "id":None, "docIds": [], "synonyms": ["Castle", "Fort", "Stronghold"], "excludeWords": []},
    {"name":"City/Village.", "id":None, "docIds": [], "synonyms": ["City", "Village", "Town"], "excludeWords": []},
    {"name":"Forest", "id":None, "docIds": [], "synonyms": ["Glade", "Woods"], "excludeWords": []},
    {"name":"Graveyard/etc.", "id":None, "docIds": [], "synonyms": ["Grave", "Tomb", "Mausoleum", "Cemetery", "Crypt"], "excludeWords": []},
    {"name":"Island", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Jungle", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Lake/Ocean", "id":None, "docIds": [], "synonyms": ["Lake", "Ocean", "Sea", "Beach", "Harbor", "Cove", "Docks"], "excludeWords": []},
    {"name":"Mountain", "id":None, "docIds": [], "synonyms": ["Cliff", "Bluff"], "excludeWords": []},
    {"name":"River", "id":None, "docIds": [], "synonyms": ["Stream", "Creek"], "excludeWords": []},
    {"name":"Ruins", "id":None, "docIds": [], "synonyms": ["Broken", "Abandoned"], "excludeWords": []},
    {"name":"Fey", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Scrub", "id":None, "docIds": [], "synonyms": ["Waste"], "excludeWords": []},
    {"name":"Sky", "id":None, "docIds": [], "synonyms": ["Air"], "excludeWords": []},
    {"name":"Tavern/Inn", "id":None, "docIds": [], "synonyms": ["Tavern", "Inn", "Bar", "Saloon"], "excludeWords": []},
    {"name":"Temple", "id":None, "docIds": [], "synonyms": ["Church", "Sacred", "Ritual"], "excludeWords": []},
    {"name":"Tower", "id":None, "docIds": [], "synonyms": ["Wizard"], "excludeWords": []},
    {"name":"Underground", "id":None, "docIds": [], "synonyms": ["Underdark", "Cave"], "excludeWords": []},
]

nextPageUrl = "http://localhost:8000/api/tags/"
while nextPageUrl is not None:
    response = requests.get(nextPageUrl, auth = ("tom", "paperless"))
    rawJson = response.json()
    log.debug(rawJson)

    tags = rawJson["results"]
    log.info("---------------------------------------------------")
    for tagToAssign in tagsToAssign:
        tagToAssign["id"] = tagIdOfName(tagToAssign["name"], tags, tagToAssign["id"])
        log.info(f"{tagToAssign["name"]}:{tagToAssign["id"]}")

    nextPageUrl = rawJson["next"]
# end while

# Scan through all the documents and assign likely tags as well as assiging the map document type to things that are not PDF
docs = 0
nextPageUrl = "http://localhost:8000/api/documents/"
mapDocuments = []
while nextPageUrl is not None and docs < maxDocsToProcess:
    pagesToUpdate = {}
    response = requests.get(nextPageUrl, auth = ("tom", "paperless"))
    rawJson = response.json()
    log.debug(rawJson)

    for docId in rawJson["all"]:
        log.debug(f"get docId {docId}")

        docResponse = requests.get(f"http://localhost:8000/api/documents/{docId}/", auth = ("tom", "paperless"))
        log.debug(docResponse)

        parsedDocResponse = json.loads(docResponse.text)
        title = parsedDocResponse["title"]
        id = parsedDocResponse["id"]
        originalFileName = parsedDocResponse["original_file_name"]

        if pathlib.Path(originalFileName).suffix.lower() != ".pdf":
            mapDocuments.append(id)

        for tagToAssign in tagsToAssign:
            #Tag if the title includes the name of the tag and one of the exclude words is not present
            if title.lower().find(tagToAssign["name"].lower()) > -1:
                excluded = False
                for excludeWord in tagToAssign["excludeWords"]:
                    if title.lower().find(excludeWord.lower()) > -1:
                        excluded = True
                        break;
                
                if not excluded:
                    if id in pagesToUpdate:
                        if tagToAssign["id"] not in pagesToUpdate[id]:
                            pagesToUpdate[id].append(tagToAssign["id"])
                    else:
                        pagesToUpdate[id] = [tagToAssign["id"]]

            #Tag if the title includes one of the synomnyms and not one of the exluded words
            for synonym in tagToAssign["synonyms"]:
                if title.lower().find(synonym.lower()) > -1:
                    excluded = False
                    for excludeWord in tagToAssign["excludeWords"]:
                        if title.lower().find(excludeWord.lower()) > -1:
                            excluded = True
                            break;

                    if id in pagesToUpdate:
                        if tagToAssign["id"] not in pagesToUpdate[id]:
                            pagesToUpdate[id].append(tagToAssign["id"])
                    else:
                        pagesToUpdate[id] = [tagToAssign["id"]]

        docs += 1
        if docs == maxDocsToProcess:
            break

        if docs % 10 == 0:
            log.info(f"processed {docs} documents")

                    
    log.info(f"Bulk update being prepared for {docs}")
    #build dictionary keyed by tag where each tag has the list of pages for the tag
    pagesByTags = {}
    for key in pagesToUpdate.keys():
        for tag in pagesToUpdate[key]:
            if tag is not None:
                if tag in pagesByTags:
                    pagesByTags[tag].append(key)
                else:
                    pagesByTags[tag] = [ key ]

    #Call bulk edit on each tag to update pages with tag
    for key in pagesByTags.keys():
        log.info(f"Bulk updating pages for tag {key} with documents {pagesByTags[key]}")
        
        body = {
            "documents": pagesByTags[key],
            "method": "modify_tags",
            "parameters": {
                "add_tags": [ key ],
                "remove_tags": []
            }
        }
        editResponse = requests.post("http://localhost:8000/api/documents/bulk_edit/", auth = ("tom", "paperless"), json = body)
        log.debug(editResponse)

        if editResponse.status_code != 200:
            log.error(f"Failed to bulk edit for tag {key}.  Full response is {editResponse}")

    #call bulk edit for the document type
    log.info(f"Bulk updating {len(mapDocuments)} documents for map document type with id {mapDocumentTypeId}. Documents: {mapDocuments}")

    body = {
        "documents": mapDocuments,
        "method": "set_document_type",
        "parameters": {
            "document_type": mapDocumentTypeId
        }
    }
    editResponse = requests.post("http://localhost:8000/api/documents/bulk_edit/", auth = ("tom", "paperless"), json = body)
    log.debug(docResponse)

    if editResponse.status_code != 200:
        log.error(f"Failed to bulk edit for map document type with id {mapDocumentTypeId}.  Full response is {editResponse}")

    nextPageUrl = rawJson["next"]
# end while
