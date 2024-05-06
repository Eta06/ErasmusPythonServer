import requests
import json


def test_new():
    url = "http://localhost:4354/new"
    data = {"name": "John", "surname": "Doe", "age": 25}
    response = requests.post(url, params={"data": json.dumps(data)})
    print(response.json())
    return response.json()['id']


def test_edit(id):
    url = "http://localhost:4354/edit"
    query = {"id": id, "key": "age", "value": 30}
    response = requests.post(url, params={"query": json.dumps(query)})
    print(response.text)


def test_get(id):
    url = "http://localhost:4354/get"
    query = {"id": id}
    response = requests.get(url, params={"query": json.dumps(query)})
    print(response.text)


if __name__ == "__main__":
    new_id = test_new()
    test_edit(new_id)
    test_get(new_id)