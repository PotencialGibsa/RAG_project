import requests
import json


def client(question):
    url = "http://192.168.1.152:8888/api/echo"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        'prompt' : question
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        print('Error with', response.status_code)
    else:
        return response.json()['answer']



if __name__ == "__main__":
    print(client('What is the name of my girlfriend?'))
