import requests

headers = {
    'Authorization': 'Basic cC5wb3BvdmFAeWNsaWVudHMudGVjaDphOTk3YzU5Mi02ZGU3LTRhMDUtYTc3ZC1kYjUwNzJmZjZiNjk=',
}



def get_prosrok():
    page = 1
    totalpages = 999999

    count = 0
    while page <= totalpages:
        url = f"https://yclients.helpdeskeddy.com/api/v2/tickets/?owner_list=0&status_list=9,v-processe,open&department_list=2,6&page={page}"
        response = requests.request("GET", url, headers=headers).json()
        isnull = response["pagination"]["total"]
        print(isnull)
        if isnull == 0:
            return 0
        elif response["data"] == []:
            return count
        else:

            for ticket_id, ticket in response["data"].items():
                if "wait_chat_fast" in ticket["tags"]:
                    count += 1
            page += 1
    return count


def get_queue():
    page = 1
    totalpages = 999999


    count = 0
    while page <= totalpages:
        url = f"https://yclients.helpdeskeddy.com/api/v2/tickets/?owner_list=0&status_list=9,v-processe,open&department_list=2,6&page={page}"
        response = requests.request("GET", url, headers=headers).json()
        totalpages = response["pagination"]["total_pages"]
        isnull = response["pagination"]["total"]
        if isnull == 0:
            return 0
        else:
            for ticket_id, ticket in response["data"].items():
                if "wait_chat_fast" not in ticket["tags"]:
                    count += 1
            page += 1
    return count


def get_open():
    page = 1
    totalpages = 999999


    count = 0
    while page <= totalpages:
        url = f"https://yclients.helpdeskeddy.com/api/v2/tickets/?status_list=9,v-processe,open&department_list=2,6&page={page}"
        response = requests.request("GET", url, headers=headers).json()
        totalpages = response["pagination"]["total_pages"]
        isnull = response["pagination"]["total"]
        if isnull == 0:
            return 0
        else:
            for ticket_id, ticket in response["data"].items():
                if ticket["owner_id"] != 0:
                    count += 1
            page += 1
    return count

def get_expert():
    page = 1
    totalpages = 999999


    count = 0
    while page <= totalpages:
        url = f"https://yclients.helpdeskeddy.com/api/v2/tickets/?status_list=9,v-processe,open&department_list=27&page={page}"
        response = requests.request("GET", url, headers=headers).json()
        count = response["pagination"]["total"]
        totalpages = response["pagination"]["total_pages"]
        # for ticket_id, ticket in response["data"].items():
        #     if ticket["owner_id"] != 0:
        #         count += 1
        page += 1
    return count
