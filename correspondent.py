import requests
def choose_correspondent(auth_credentials):
    page_url = "http://localhost:8000/api/correspondents/?full_perms=true"
    print("\n\n")
    row = 0
    while page_url is not None:
        response = requests.get(page_url, auth=auth_credentials)
        raw_json = response.json()
        log.debug(raw_json)

        for correspondent in raw_json["results"]:
            data = f"{correspondent['id']:02d}: {correspondent['name']}".ljust(40)
            if row % 2 == 0:
                print(f"{data}\t", end="")
            else:
                print(f"{data}")

            row += 1
        page_url = raw_json["next"]

    print("")
    selected_correspondent = input("Which correspondent should be assigned (0 for none)?")
    return selected_correspondent