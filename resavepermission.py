import requests
import json
import re
from config import lead_headers

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
        salon, user = parselink(url)
        data = getpermission(salon, user)
        status = putpermission(salon, user, data)
        print(status)
        if status == True:
            return True
        else:
            return False
    else:
        print("not valid")
        return False

def getpermission(salon, link):
    url = f"https://api.yclients.com/api/v1/company/{salon}/users/{link}/permissions"
    payload = {}
    response = requests.request("GET", url, headers=lead_headers, data=payload).json()
    return response["data"]

def putpermission(salon, user, data):
    url = f"https://api.yclients.com/api/v1/company/{salon}/users/{user}/permissions"
    payload = json.dumps(data)
    response = requests.request("PUT", url, headers=lead_headers, data=payload)
    status = response.json()
    if response.status_code == 200:
        return status['success']