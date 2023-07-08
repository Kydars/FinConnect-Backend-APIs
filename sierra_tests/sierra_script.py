import requests
import json

LOGIN_URL = 'https://afzpve4n13.execute-api.ap-southeast-2.amazonaws.com/login'
def get_token() -> str:
    token = ''
    body = {
        "username": "F14A_SIERRA",
        "password": "sigma",
        "group": "F14A_SIERRA"
    }
    try:
        response = requests.post(LOGIN_URL, json=body)
        response_obj = json.loads(response.text)
        if response_obj:
            token = response_obj['token']

    except Exception:
        print('Could not retrieve token')
    return token

if __name__ == "__main__":
    token = get_token()
    simlify = []
    detail = []
    r = requests.get("https://afzpve4n13.execute-api.ap-southeast-2.amazonaws.com/F14A_SIERRA/test_service_F12_ZULU", headers ={"Authorization":token})
    if(r.status_code == 200):
        simlify = r.json()["result"]
    else:
        print("Can not Pind test service, check with tester provider")

    r = requests.get("https://afzpve4n13.execute-api.ap-southeast-2.amazonaws.com/F14A_SIERRA/test_service_F12_ZULU?detail=True", headers ={"Authorization":token})
    if(r.status_code == 200):
        detail = r.json()["result"]
    else:
        print("Can not Pind test service, check with tester provider")
    total = 0
    success = 0
    for x in detail:
        if x["success_status"] == True:
            success += 1
        total += 1

    print("The test tests " + str(total) + " scenario and the pass result is " + str(success) + "/" + str(total) + ".")

    for x in simlify:
        print(x)
    for x in detail:
        print(x)
