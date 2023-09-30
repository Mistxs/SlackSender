import logging

import requests
import json
import re
from config import lead_headers

logger = logging.getLogger('rsfp_logger')

handler = logging.FileHandler('rsfp.log')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)

logger.addHandler(handler)


def parselink(url):
    salon_match = re.search(r"/edit/(\d+)/", url)
    user_match = re.search(r"/(\d+)/\?page", url)
    if salon_match and user_match:
        salon = salon_match.group(1)
        user = user_match.group(1)
        return salon, user
    else:
        return False

def resavepermission(url):
    if parselink(url):
        logger.info(f'ResafePermission started. Link - {url}')
        salon, user = parselink(url)
        logger.info(f'Parselink done. Salon = {salon}, user = {user}')
        data = getpermission(salon, user)
        status = putpermission(salon, user, data)
        print("Status", status["success"])
        if status["success"] == True:
            return True
        else:
            return False
    else:
        logger.warning(f'Parselink: Error. Link {url} is not valid')
        print("not valid")
        return False

def getpermission(salon, link):
    url = f"https://api.yclients.com/api/v1/company/{salon}/users/{link}/permissions"
    payload = {}
    logger.info(f'Start getpermission. URL: {url}')
    response = requests.request("GET", url, headers=lead_headers, data=payload).json()
    logger.info(f'Getpermission: response - {response}')
    return response["data"]

def putpermission(salon, user, data):
    url = f"https://api.yclients.com/api/v1/company/{salon}/users/{user}/permissions"

    payload = json.dumps(data)
    logger.info(f'Start putpermission with payload: {payload}')
    response = requests.request("PUT", url, headers=lead_headers, data=payload)
    status = response.json()
    logger.info(f'Putpermission: response - {status}')
    return status