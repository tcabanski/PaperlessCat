import requests
import sys
import logging

tags_to_assign = [
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
    {"name":"Castle/Fort/etc.", "id":None, "docIds": [], "synonyms": ["Castle", "Fort", "Stronghold", "Gate", "Rampart", "Wall", "Keep", "Throne"], "excludeWords": []},
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
    {"name":"Temple", "id":None, "docIds": [], "synonyms": ["Church", "Chapel", "Sacred", "Ritual"], "excludeWords": []},
    {"name":"Tower", "id":None, "docIds": [], "synonyms": ["Wizard"], "excludeWords": []},
    {"name":"Underground", "id":None, "docIds": [], "synonyms": ["Underdark", "Cave", "Sewer"], "excludeWords": []},
    {"name":"Shop", "id":None, "docIds": [], "synonyms": ["Apothecary", "Blacksmith", "Market"], "excludeWords": []},
    {"name":"Road", "id":None, "docIds": [], "synonyms": ["Highway", "Path"], "excludeWords": []},
    {"name":"Lab", "id":None, "docIds": [], "synonyms": ["Alchemist", "Alchemical", "Potion", "Apothecary"], "excludeWords": []},
    {"name":"Swamp", "id":None, "docIds": [], "synonyms": ["Bog", "Marsh", "Fen"], "excludeWords": []},
    {"name":"Phased", "id":None, "docIds": [], "synonyms": ["phase"], "excludeWords": []}
]

def check_tags(tags_to_assign):
    for tag_to_assign in tags_to_assign:
        if tag_to_assign["id"] is None:
            tag_to_assign = f"Tag {tag_to_assign['name']} was not found in paperless!"
            log.error(tag_to_assign)
            sys.exit("EXITING: " + tag_to_assign)

def tag_id_of_name(name, tags, oldId):
    for tag in tags:
        if tag["name"] == name:
            return tag["id"]
        
    return oldId

def validate_tags(AUTH_CREDENTIALS):
    log = logging.getLogger("global")
    page_url = "http://localhost:8000/api/tags/"
    while page_url is not None:
        response = requests.get(page_url, auth=AUTH_CREDENTIALS)
        raw_json = response.json()
        log.debug(raw_json)

        tags = raw_json["results"]
        for tag_to_assign in tags_to_assign:
            tag_to_assign["id"] = tag_id_of_name(tag_to_assign["name"], tags, tag_to_assign["id"])
        page_url = raw_json["next"]

    for tag_to_assign in tags_to_assign:
        log.info(f"{tag_to_assign['name']}:{tag_to_assign['id']}")

    check_tags()