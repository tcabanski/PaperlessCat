import json

def get_credentials():
    json_file_path = "./.secrets/credentials.json"
    with open(json_file_path, "r") as f:
        credentials = json.load(f)
        
    return (credentials["username"], credentials["password"])