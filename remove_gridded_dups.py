import requests
import re
from collections import namedtuple
import logging
import pathlib
from document import Document
import difflib

log = logging.getLogger("global")
console = logging.StreamHandler()
formatter =  logging.Formatter('%(asctime)s %(levelname)s : %(message)s')
console.setFormatter(formatter)
log.addHandler(console)
log.setLevel(logging.INFO)
log.info("Starting")

equivalent_diffs = [
    "+no",
    "+non",
    "+un",
    "-grid",
    "-gridded"
]
longest_diff = len(max(equivalent_diffs, key=len)) + 5  


#config
map_document_type_id = 1
grid_tag_id = 34
AUTH_CREDENTIALS = ("tom", "paperless")

# Scan through all the documents and find gridded duplicates
docs = 0
page_url = "http://localhost:8000/api/documents/?document_type=1"
#page_url = "http://localhost:8000/api/documents/?page=1&page_size=50&ordering=-added&truncate_content=true&title__icontains=120%20ppi%20-%2054%20x%2030%20-%20mausoleum%20inside"


without_grid = []
with_grid = []
candidates_to_delete = []
response = requests.get(page_url, auth = AUTH_CREDENTIALS)
raw_json = response.json()
log.debug(raw_json)

doc_count = len(raw_json["all"])
log.info(f"Reading {doc_count} maps")

page_url += "&page_size=10000"
while page_url is not None:
    response = requests.get(page_url, auth = AUTH_CREDENTIALS)
    raw_json = response.json()
    log.debug(raw_json)

    for doc_result in raw_json["results"]:
        doc = Document(doc_result["id"], doc_result["title"].lower(), doc_result["original_file_name"].lower(), 
                       grid_tag_id in doc_result["tags"], 0)
        if (doc.has_grid_tag):
            with_grid.append(doc)
        else:
            without_grid.append(doc)
        #end if
        
        docs += 1
    #end for
        
    page_url = raw_json["next"]
    log.info(f"Read {docs} of {doc_count} maps")
#end while
log.info(f"Read {docs} of {doc_count} maps and found {len(with_grid)} with grid")

log.info(f"Looking for gridded duplicates that can be deleted among {len(with_grid)} gridded candidates")

# todo: I believe this is too narrow and will not be able to handle cases where no gets added with things like dashes.  It could be as simple as adding the right specs to the delta list but I am not sure about that.
docs = 0
doc_count = len(with_grid)
for grid_doc in with_grid:
    grid_doc_extension = pathlib.Path(grid_doc.file_name).suffix.lower()
    grid_doc_length = len(grid_doc.file_name)
    no_grid_count = 0
    log.info(f"Processing gridded map {docs + 1} of {len(with_grid)} for non-gridded duplicates.  Scanning {len(without_grid)} maps without grids.")
    for no_grid_doc in without_grid:
        fn_len = len(no_grid_doc.file_name)
        if not (fn_len > grid_doc_length + longest_diff or fn_len < grid_doc_length - longest_diff or pathlib.Path(no_grid_doc.file_name).suffix.lower() != grid_doc_extension):
            delta_list = [diff for diff in difflib.ndiff(grid_doc.title, no_grid_doc.title) if diff[0] != ' ']
            if len(delta_list) > 0:
                consolidated_delta_list = []
                mode = delta_list[0][0]
                spec = ""
                for item in delta_list:
                    if item[0] == mode:
                        spec += item[2:]
                    else:
                        consolidated_delta_list.append(mode + spec)
                        spec = item[2:]
                        mode = item[0]
                    #end if
                #end for
                if len(spec) > 0:
                    consolidated_delta_list.append(mode + spec)
                #end if
                if (len(consolidated_delta_list) == 1):
                    for diff in equivalent_diffs:
                        if diff in consolidated_delta_list:
                            grid_doc.non_grid_duplicate_id = no_grid_doc.id
                            candidates_to_delete.append(grid_doc)
                            break;
                        #end if
                    #end for
                #end if
            #end if
        #end if
    
        no_grid_count += 1  
        if no_grid_count % 10000 == 0:
            log.info(f"Scanned {no_grid_count} of {len(without_grid)} without grid for gridded map {docs + 1} of {len(with_grid)}")
        #end if
    #end for
    docs += 1  
    if docs % 2 == 0:
        log.info(f"Processed {docs} of {len(with_grid)} gridded maps")
        break
    #end if 
#end for
            
log.info(f"Processed {docs} of {doc_count} maps with grids")             
log.info(f"Found {len(candidates_to_delete)} maps with grids to delete")
                
                              

    
