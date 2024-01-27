import requests
from collections import namedtuple
import json
import logging

log = logging.getLogger("global")
console = logging.StreamHandler()
formatter =  logging.Formatter('%(asctime)s %(levelname)s : %(message)s')
console.setFormatter(formatter)
log.addHandler(console)
log.setLevel(logging.INFO)
log.info("Starting")

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
    {"name":"Blood", "id":None, "docIds": [], "synonyms": [], "excludeWords": []}
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

# Scan through all the documents and assign likely tags
maxDocs = 100
docs = 0
nextPageUrl = "http://localhost:8000/api/documents/"
while nextPageUrl is not None and docs < maxDocs:
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
        if docs == maxDocs:
            break

        if docs % 10 == 0:
            log.info(f"processed {docs} documents")

                    
    log.info(f"Bulk update being prepared for {docs}")
    #build dictionary keyed by tag where each tag has the list of pages for the tag
    pagesByTags = {}
    for key in pagesToUpdate.keys():
        for tag in pagesToUpdate[key]:
            if tag in pagesByTags:
                pagesByTags[tag].append(key)
            else:
                pagesByTags[tag] = [ key ]

    for key in pagesByTags.keys(): 
        log.info(f"{key}:{pagesByTags[key]}")

    nextPageUrl = rawJson["next"]
# end while
