import os
import logging

API_HOST = os.getenv('PAPERLESS_HOST')

def validate():
    log = logging.getLogger("global")
    if API_HOST == None:
        log.error("Have to set PAPERLESS_HOST in environment")
