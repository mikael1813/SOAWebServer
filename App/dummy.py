import time

import requests
import json

if __name__ == "__main__":
    # api_url = 'http://localhost:5000/user/login'
    # create_row_data = {'mail_or_token': 'mai@as.c',
    #                    'password': 'fawonflaiks'}
    # print(create_row_data)
    # r = requests.get(url=api_url, json=create_row_data)
    # print(r.status_code, r.reason, r.text)
    # token = json.loads(r.text)
    # print(token)
    # token = token["token"]
    #
    # row_data = {'mail_or_token': token, 'password': ''}
    # print(row_data)
    # time.sleep(4)
    # r = requests.get(url=api_url, json=row_data)
    # print(r.status_code, r.reason, r.text)

    # create_row_data = {'mail_or_token': 'mai@as.c',
    #                    'password': 'fawonflaiks'}
    # api_url = 'http://localhost:5000/orders'
    # r = requests.get(url=api_url, json=create_row_data)
    # print(r.status_code, r.reason, r.text)

    create_row_data = {'mail_or_token': 'mai@as.c',
                       'password': 'fawonflaiks'}
    api_url = 'http://localhost:5000/menu'
    r = requests.get(url=api_url, json=create_row_data)
    print(r.status_code, r.reason, r.text)
