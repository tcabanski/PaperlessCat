import requests
import logging
import os
import platform
import constants

def choose_correspondent(auth_credentials):
    os.system("mode 200,100")
    log = logging.getLogger("global")
    base_url = f"http://{constants.API_HOST}:8000/api/correspondents/?full_perms=true"
    print("\n\n")

    def clear_console():
        system = platform.system()
        if system == 'Windows':
            os.system('cls')
        elif system == 'Linux' or system == 'Darwin':
            os.system('clear')
        else:
            print("Operating system not supported.")

    def display_correspondents(correspondents):
        clear_console()
        item = 0
        for correspondent in correspondents:
            data = f"{correspondent['id']:03d}: {correspondent['name']}".ljust(30)[0:30]
            if item > 0 and item % 5 == 0:
                print()
            print(f"{data}\t", end="")
            item += 1
        print("")

    def fetch_correspondents(url):
        response = requests.get(url, auth=auth_credentials)
        raw_json = response.json()
        log.debug(raw_json)
        return raw_json

    def search_correspondents(query, correspondents):
        return [c for c in correspondents if c['name'].lower().startswith(query.lower())]

    correspondents = []
    page_url = base_url
    while page_url is not None:
        raw_json = fetch_correspondents(page_url)
        correspondents.extend(raw_json["results"])
        page_url = raw_json["next"]

    while True:
        display_correspondents(correspondents)
        user_input = input("Enter correspondent number, part of a name, or 'reset' to start over (0 for none): ").strip()

        if user_input.isnumeric():
            # Handle numeric input
            if int(user_input) == 0:
                return "0"
            matching_correspondents = [c for c in correspondents if c['id'] == int(user_input)]
            if matching_correspondents:
                return str(matching_correspondents[0]['id'])
            else:
                print("No correspondent found with that ID. Try again.")
        elif user_input.lower() == "reset":
            # Reset the process
            print("Resetting selection process...\n")
            continue
        else:
            # Handle partial name input
            matches = search_correspondents(user_input, correspondents)
            if not matches:
                print("No matches found. Try again.")
            elif len(matches) == 1:
                # If only one match, return its ID
                return str(matches[0]['id'])
            else:
                # If multiple matches, display only the matched list
                print("\nMultiple matches found:")
                display_correspondents(matches)
                while True:
                    match_input = input("Type the exact number of the correspondent or 'reset' to start over: ").strip()
                    if match_input.isnumeric():
                        selected_match = [c for c in matches if c['id'] == int(match_input)]
                        if selected_match:
                            return str(selected_match[0]['id'])
                        else:
                            print("Invalid number. Please select from the displayed matches.")
                    elif match_input.lower() == "reset":
                        print("Resetting selection process...\n")
                        break
                    else:
                        print("Invalid input. Please type a number or 'reset'.")

def get_correspondant_name(id, auth_credentials):
    if not id.isnumeric():
        raise Exception("Input must be numeric") 
    
    if int(id) == 0:
        return "NONE"
    
    log = logging.getLogger("global")
    response = requests.get(f"http://{constants.API_HOST}:8000/api/correspondents/?id={id}", auth = auth_credentials)
    raw_json = response.json()
    log.debug(raw_json)

    if response.status_code != 200:
        log.error(f"Failed to get correspondant for id {id}.  Error is {response.reason}")

    correspondant = raw_json["results"][0]
    return correspondant["name"]