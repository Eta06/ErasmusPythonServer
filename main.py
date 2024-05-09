from bson import ObjectId
import cv2
from flask import Flask, request, render_template, Response
from flask_cors import CORS

import pymongo
import json

camera = cv2.VideoCapture(0)  # 0 is the default camera

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["erasmus"]
collection = db["erasmusapp"]

# Create Flask app
app = Flask(__name__)
CORS(app)


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


def gen_frames():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)  # 0 is the default camera

    while True:
        success, frame = camera.read()  # Read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Concat frame one by one and show result

    if camera is not None:
        camera.release()
        camera = None


@app.route('/streamdata')
def stream():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/stream")
def streamtest():
    return render_template("stream.html", username="Emir")

@app.route("/activity", methods=["POST", "GET"])
def activity():
    id = request.cookies.get("id")

    if id:
        result = collection.find_one({"_id": ObjectId(id)})
        # Get the last activity from the MongoDB
        try:
            activities = result["activities"]
            print(activities)
            return render_template("activity.html", activities=activities, username=result["name"])
        except KeyError:
            return render_template("activity.html", activities=[], username=result["name"])
        except:
            return render_template("activity.html", activities=[], username=result["name"])

    return render_template("index.html", message="User not found")

@app.route("/", methods=["POST", "GET"])
def home():
    # Check if id cookie exists
    id = request.cookies.get("id")
    if id:
        # search the database with the id
        result = collection.find_one({"_id": ObjectId(id)})
        if result:
            # Return the main page with the user's information
            return render_template("mainpage.html", username=result["name"], surname=result["surname"], id=id, balance=result["balance"])

    if request.method == "POST":
        data = request.form
        name = data.get("name")
        surname = data.get("surname")

        # Check if user exists with only name
        result = collection.find_one({"name": name, "surname": surname})
        print(result)

        if result:
            # Save id to browser cookie and return the main page
            response = render_template("mainpage.html", username=name, surname=surname, id=str(result["_id"]), message="", balance=result["balance"])
            return response
        else:
            # Redirect the user to index.html with a message
            return render_template("index.html", message="User not found")
    return render_template("index.html", message="")


@app.route("/addtest", methods=["POST", "GET"])
def addtest():
    # Create a new user with name Emir and surname Alim and add activities list and also a age to the user
    collection.insert_one({"name": "Emir", "surname": "Alim", "activities": ["01.01.2024", "01.02.2024"], "age": 20})

if __name__ == '__main__':
    app.run(debug=True, port=4354, host="0.0.0.0")
