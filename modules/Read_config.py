import json


def read_config(path = './config.json'):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    return data


if __name__ == "__main__":
    read_config()