from bson import ObjectId
from flask import Flask, request, jsonify
import pymongo
import json


# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["erasmus"]
collection = db["erasmusapp"]

# Create Flask app
app = Flask(__name__)


@app.route("/edit", methods=["POST", "GET"])
def api():
    query = request.args.get("query")
    query = json.loads(query)
    id = query.get("id")
    key = query.get("key")
    value = query.get("value")
    result = collection.find_one({"_id": ObjectId(id)})
    print(result)
    if result:
        result[key] = value
        collection.update_one({"_id": ObjectId(id)}, {"$set": result})
        return {"status": "success"}
    else:
        return {"status": "failed"}


@app.route("/new", methods=["POST", "GET"])
def new():
    data = request.args.get("data")
    data = json.loads(data)
    if "name" not in data or "surname" not in data or "age" not in data:
        return "Missing data"
    name = data["name"]
    surname = data["surname"]
    age = data["age"]
    mydict = {"name": name, "surname": surname, "age": age, "balance": 0, "activities": []}
    collection.insert_one(mydict)
    return {"id": str(mydict["_id"])}


@app.route("/get", methods=["POST", "GET"])
def get():
    query = request.args.get("query")
    query = json.loads(query)
    id = query.get("id")
    result = collection.find_one({"_id": ObjectId(id)})
    if result:
        return {
            "name": result["name"],
            "surname": result["surname"],
            "age": result["age"],
            "balance": result["balance"],
            "activities": result["activities"]
        }
    else:
        return {"status": "failed"}


if __name__ == '__main__':
    app.run(debug=True,port=4354)