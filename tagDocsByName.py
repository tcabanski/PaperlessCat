import requests
from collections import namedtuple
import json
import logging
import pathlib
import sys

log = logging.getLogger("global")
console = logging.StreamHandler()
formatter =  logging.Formatter('%(asctime)s %(levelname)s : %(message)s')
console.setFormatter(formatter)
log.addHandler(console)
log.setLevel(logging.INFO)
log.info("Starting")

#config
mapDocumentTypeId = 1
pdfDocumentTypeId = 13
maxDocsToProcess = 999000
onlyProcessEmptyDocType = True

def tagIdOfName(name, tags, oldId):
    for tag in tags:
        if tag["name"] == name:
            return tag["id"]
        
    return oldId

# Find the ID of key tags
tagsToAssign = [
    {"name":"Grid", "id": None, "docIds": [], "synonyms": [], "excludeWords": ["No", "Non", "less"]},
    {"name":"Night", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Snow", "id":None, "docIds": [], "synonyms": ["Winter"], "excludeWords": []},
    {"name":"Rain", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Fog", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Lava", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Fire", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Desert", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Astral", "id":None, "docIds": [], "synonyms": ["Asteroid", "Starship", "Star", "Planet", "Alien", "SciFi", "Space", "Orbital"], "excludeWords": []},
    {"name":"Blood", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Bridge", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Camp", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Castle/Fort/etc.", "id":None, "docIds": [], "synonyms": ["Castle", "Fort", "Stronghold", "Gate", "Rampart", "Wall", "Keep"], "excludeWords": []},
    {"name":"City/Village", "id":None, "docIds": [], "synonyms": ["City", "Village", "Town"], "excludeWords": []},
    {"name":"Forest", "id":None, "docIds": [], "synonyms": ["Glade", "Woods"], "excludeWords": []},
    {"name":"Graveyard/etc.", "id":None, "docIds": [], "synonyms": ["Grave", "Tomb", "Mausoleum", "Cemetery", "Crypt"], "excludeWords": []},
    {"name":"Island", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Jungle", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Lake/Ocean", "id":None, "docIds": [], "synonyms": ["Lake", "Ocean", "Sea", "Beach", "Harbor", "Cove", "Dock", "Flood", "Pier"], "excludeWords": []},
    {"name":"Mountain", "id":None, "docIds": [], "synonyms": ["Cliff", "Bluff"], "excludeWords": []},
    {"name":"River", "id":None, "docIds": [], "synonyms": ["Stream", "Creek"], "excludeWords": []},
    {"name":"Ruins", "id":None, "docIds": [], "synonyms": ["Broken", "Abandoned", "Ruin"], "excludeWords": []},
    {"name":"Fey", "id":None, "docIds": [], "synonyms": [], "excludeWords": []},
    {"name":"Scrub", "id":None, "docIds": [], "synonyms": ["Waste"], "excludeWords": []},
    {"name":"Sky", "id":None, "docIds": [], "synonyms": ["Air"], "excludeWords": []},
    {"name":"Tavern/Inn", "id":None, "docIds": [], "synonyms": ["Tavern", "Inn", "Bar", "Saloon"], "excludeWords": []},
    {"name":"Temple", "id":None, "docIds": [], "synonyms": ["Church", "Sacred", "Ritual"], "excludeWords": []},
    {"name":"Tower", "id":None, "docIds": [], "synonyms": ["Wizard"], "excludeWords": []},
    {"name":"Underground", "id":None, "docIds": [], "synonyms": ["Underdark", "Cave", "Sewer"], "excludeWords": []},
    {"name":"Shop", "id":None, "docIds": [], "synonyms": ["Apothecary", "Blacksmith", "Market"], "excludeWords": []},
    {"name":"Road", "id":None, "docIds": [], "synonyms": ["Highway"], "excludeWords": []},
    {"name":"Lab", "id":None, "docIds": [], "synonyms": ["Alchemist", "Alchemical", "Potion", "Apothecary"], "excludeWords": []},
    {"name":"Swamp", "id":None, "docIds": [], "synonyms": ["Bog", "Marsh", "Fen"], "excludeWords": []},
    {"name":"Phased", "id":None, "docIds": [], "synonyms": ["phase"], "excludeWords": []}
]

pageUrl = "http://localhost:8000/api/tags/"
while pageUrl is not None:
    response = requests.get(pageUrl, auth = ("tom", "paperless"))
    rawJson = response.json()
    log.debug(rawJson)

    tags = rawJson["results"]
    for tagToAssign in tagsToAssign:
        tagToAssign["id"] = tagIdOfName(tagToAssign["name"], tags, tagToAssign["id"])
    #end for

    pageUrl = rawJson["next"]
# end while
    
for tagToAssign in tagsToAssign:
    log.info(f"{tagToAssign["name"]}:{tagToAssign["id"]}")
#end for

# validate that all tags have assigned paperless ids
for tagToAssign in tagsToAssign:
    if tagToAssign["id"] is None:
        errorMessage = f"Tag {tagToAssign["name"]} was not found in paperless!"
        log.error(errorMessage)
        sys.exit("EXITING: " + errorMessage)

# get the list of correspondents and let the user choose one to assign (or none)
pageUrl = "http://localhost:8000/api/correspondents/?full_perms=true"
print("\n\n")
row = 0
while pageUrl is not None:
    response = requests.get(pageUrl, auth = ("tom", "paperless"))
    rawJson = response.json()
    log.debug(rawJson)

    for correspondent in rawJson["results"]:
        data = f"{correspondent["id"]:02d}: {correspondent["name"]}".ljust(40)
        if row % 2 == 0: 
            print(f"{data}\t", end = "") 
        else:
            print(f"{data}")

        row += 1
        #end if
    #end for 
    
    pageUrl = rawJson["next"]
#end while

print("")
selectedCorrespondent = input("Which correspondent should be assigned (0 for none)?")

# Scan through all the documents and assign likely tags as well as assiging the map document type to things that are not PDF
docs = 0
if onlyProcessEmptyDocType:
    pageUrl = "http://localhost:8000/api/documents/?document_type__isnull=1&page_size=100000"
else:
    pageUrl = "http://localhost:8000/api/documents/?sort=added&page-size=100000"

mapDocuments = []
pdfDocuments = []
allDocuments = []
pagesToUpdate = {}
response = requests.get(pageUrl, auth = ("tom", "paperless"))
rawJson = response.json()
log.debug(rawJson)

docsToProcess = len(rawJson["all"])
log.info(f"Processing {docsToProcess} documents")

while pageUrl is not None:
    response = requests.get(pageUrl, auth = ("tom", "paperless"))
    rawJson = response.json()
    log.debug(rawJson)

    for docResult in rawJson["results"]:
        docId = docResult["id"]
        log.debug(f"processing docId {docId}")

        title = docResult["title"]
        originalFileName = docResult["original_file_name"]

        allDocuments.append(docId)

        if pathlib.Path(originalFileName).suffix.lower() != ".pdf":
            mapDocuments.append(docId)
        #end if
        
        if pathlib.Path(originalFileName).suffix.lower() == ".pdf":
            pdfDocuments.append(docId)
        #end if

        for tagToAssign in tagsToAssign:
            #Tag if the title includes the name of the tag and one of the exclude words is not present
            if title.lower().find(tagToAssign["name"].lower()) > -1:
                excluded = False
                for excludeWord in tagToAssign["excludeWords"]:
                    if title.lower().find(excludeWord.lower()) > -1:
                        excluded = True
                        break;
                #end for
                
                if not excluded:
                    if id in pagesToUpdate:
                        if tagToAssign["id"] not in pagesToUpdate[docId]:
                            pagesToUpdate[docId].append(tagToAssign["id"])
                    else:
                        pagesToUpdate[docId] = [tagToAssign["id"]]
                    #end if
                #end if
            #end if

            #Tag if the title includes one of the synomnyms and not one of the exluded words
            for synonym in tagToAssign["synonyms"]:
                if title.lower().find(synonym.lower()) > -1:
                    excluded = False
                    for excludeWord in tagToAssign["excludeWords"]:
                        if title.lower().find(excludeWord.lower()) > -1:
                            excluded = True
                            break;
                    #end for

                    if id in pagesToUpdate:
                        if tagToAssign["id"] not in pagesToUpdate[id]:
                            pagesToUpdate[docId].append(tagToAssign["id"])
                    else:
                        pagesToUpdate[docId] = [tagToAssign["id"]]
            #end for
        #end for

        docs += 1
        if docs == maxDocsToProcess:
            break
    #end for
        
    pageUrl = rawJson["next"]
    log.info(f"processed {docs} of {docsToProcess} documents")
#end while
               
log.info(f"Processing complete. Bulk update being prepared for {docs} documents")
#build dictionary keyed by tag where each tag has the list of pages for the tag
pagesByTags = {}
for key in pagesToUpdate.keys():
    for tagToAssign in pagesToUpdate[key]:
        if tagToAssign is not None:
            if tagToAssign in pagesByTags:
                pagesByTags[tagToAssign].append(key)
            else:
                pagesByTags[tagToAssign] = [ key ]
#end for

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
        log.error(f"Failed to bulk edit for tag {key}.  Error is {editResponse.reason}")
#end for
        
#call bulk edit for the correspondent
if int(selectedCorrespondent) != 0:
    log.info(f"Bulk updating {len(allDocuments)} documents for correspondent with id {selectedCorrespondent}. Documents: {allDocuments}")

    body = {
        "documents": allDocuments,
        "method": "set_correspondent",
        "parameters": {
            "correspondent": int(selectedCorrespondent)
        }
    }
    editResponse = requests.post("http://localhost:8000/api/documents/bulk_edit/", auth = ("tom", "paperless"), json = body)
    log.debug(editResponse)

    if editResponse.status_code != 200:
        log.error(f"Failed to bulk edit for correspondent with id {selectedCorrespondent}.  Error is {editResponse.reason}")
#end if

#call bulk edit for the map document type
log.info(f"Bulk updating {len(mapDocuments)} documents for map document type with id {mapDocumentTypeId}. Documents: {mapDocuments}")

body = {
    "documents": mapDocuments,
    "method": "set_document_type",
    "parameters": {
        "document_type": mapDocumentTypeId
    }
}
editResponse = requests.post("http://localhost:8000/api/documents/bulk_edit/", auth = ("tom", "paperless"), json = body)
log.debug(editResponse)

if editResponse.status_code != 200:
    log.error(f"Failed to bulk edit for map document type with id {mapDocumentTypeId}.  Error is {editResponse.reason}")

#call bulk edit for the pdf document type
log.info(f"Bulk updating {len(pdfDocuments)} documents for uncategorized document type with id {pdfDocumentTypeId}. Documents: {pdfDocuments}")

body = {
    "documents": pdfDocuments,
    "method": "set_document_type",
    "parameters": {
        "document_type": pdfDocumentTypeId
    }
}
editResponse = requests.post("http://localhost:8000/api/documents/bulk_edit/", auth = ("tom", "paperless"), json = body)
log.debug(editResponse)

if editResponse.status_code != 200:
    log.error(f"Failed to bulk edit for uncategorized document type with id {pdfDocumentTypeId}.  Error is {editResponse.reason}")
