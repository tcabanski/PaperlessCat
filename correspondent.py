import requests
import logging
import os

def choose_correspondent(auth_credentials):
    os.system("mode 200,100")
    log = logging.getLogger("global")
    page_url = "http://jittikun:8000/api/correspondents/?full_perms=true"
    print("\n\n")
    item = 0
    while page_url is not None:
        response = requests.get(page_url, auth=auth_credentials)
        raw_json = response.json()
        log.debug(raw_json)

        for correspondent in raw_json["results"]:
            data = f"{correspondent['id']:03d}: {correspondent['name']}".ljust(30)[0:30]
            if item > 0 and item % 4 == 0:
                print()
            print(f"{data}\t", end="")

            item += 1
        page_url = raw_json["next"]

    print("")
    selected_correspondent = input("Which correspondent should be assigned (0 for none)?")
    return selected_correspondent

def get_correspondant_name(id, auth_credentials):
    if not id.isnumeric():
        raise Exception("Input must be numeric") 
    
    if int(id) == 0:
        return "NONE"
    
    log = logging.getLogger("global")
    response = requests.get(f"http://jittikun:8000/api/correspondents/?id={id}", auth = auth_credentials)
    raw_json = response.json()
    log.debug(raw_json)

    if response.status_code != 200:
        log.error(f"Failed to get correspondant for id {id}.  Error is {response.reason}")

    correspondant = raw_json["results"][0]
    return correspondant["name"]