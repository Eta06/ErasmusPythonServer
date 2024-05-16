from bson import ObjectId
from werkzeug.utils import secure_filename
import cv2
from flask import Flask, request, render_template, Response
from flask_cors import CORS

import pymongo
import json
import os


camera = cv2.VideoCapture(1)  # 0 is the default camera
success, frame = False, None

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


import time
from deepface import DeepFace


lastuser = None

def gen_frames():
    global camera
    global frame
    global success
    if camera is None:
        camera = cv2.VideoCapture(2)  # 0 is the default camera
    last_time = time.time()
    while True:
        success, frame = camera.read()  # Read the camera frame
        if not success:
            break
        if time.time() - last_time > 1:
            last_time = time.time()
            result = DeepFace.find(frame, db_path="images", enforce_detection=False, silent=True)
            idendity = result[0]["identity"].to_list()
            if idendity:
                human = idendity[0]
                stop = human.rindex("\\")
                id = human[7:stop]
                # id ye gore gerekli islemleri yapariz
                print("passenger found", id)
                global lastuser
                if lastuser == id:
                    print("same user")
                    with open("doorstatus.txt", "w") as file:
                        file.write("open")
                else:
                    lastuser = id
                    with open("lastuser.json", "w") as file:
                        json.dump({"lastuser": id}, file)
                    with open("doorstatus.txt", "w") as file:
                        file.write("open")

            else:
                print("no passenger found")
                with open("lastuser.json", "w") as file:
                    json.dump({"lastuser": "Not Found"}, file)
                with open("doorstatus.txt", "w") as file:
                    file.write("close")

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
            return render_template("mainpage.html", username=result["name"], surname=result["surname"], id=id,
                                   balance=result["balance"])

    if request.method == "POST":
        data = request.form
        name = data.get("name")
        surname = data.get("surname")

        # Check if user exists with only name
        result = collection.find_one({"name": name, "surname": surname})
        print(result)

        if result:
            # Save id to browser cookie and return the main page
            response = render_template("mainpage.html", username=name, surname=surname, id=str(result["_id"]),
                                       message="", balance=result["balance"])
            return response
        else:
            # Redirect the user to index.html with a message
            return render_template("index.html", message="User not found")
    return render_template("index.html", message="")


@app.route("/getlastuser", methods=["POST", "GET"])
def lastuser():
    with open("lastuser.json", "r") as file:
        lastuser_data = json.load(file)
    lastuser = lastuser_data.get("lastuser")
    return lastuser


@app.route("/doorcontrol", methods=["POST", "GET"])
def doorcontrol():
    with open("doorstatus.txt", "r") as file:
        status = file.read()
    return status


@app.route("/addtest",  methods=["POST", "GET"])
def addtest():
    # Create a new user with name Emir and surname Alim and add activities list and also a age to the user
    collection.insert_one({"name": "Emir", "surname": "Alim", "activities": ["01.01.2024", "01.02.2024"], "age": 20})


from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'images'  # Folder to store uploaded images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        try:
            data = request.form
            name = data.get("name")
            surname = data.get("surname")
            age = int(data.get("age"))

            # 1. Handle File Upload
            if 'file' not in request.files:
                raise Exception("No file part")
            file = request.files['file']
            if file.filename == '':
                raise Exception("No selected file")
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)

                # 2. Check for Existing User
                existing_user = collection.find_one({"name": name, "surname": surname})
                if existing_user:
                    raise Exception("User already exists")

                # 3. Store User Data in MongoDB (without image path)
                user_data = {
                    "name": name,
                    "surname": surname,
                    "age": age,
                    "balance": 0,
                    "activities": []
                }
                result = collection.insert_one(user_data)
                user_id = result.inserted_id


                # 4. Create User-Specific Image Folder and Save
                user_image_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
                os.makedirs(user_image_folder, exist_ok=True)
                filepath = os.path.join(user_image_folder, filename)
                file.save(filepath)

                # 5. Update User Data in MongoDB with Image Path
                collection.update_one({"_id": user_id}, {"$set": {"image_path": filepath}})

                # 6. Set Cookie and Redirect
                response = render_template("mainpage.html", username=name, surname=surname,
                                           id=str(user_id), balance=0)
                response.set_cookie("id", str(user_id))
                return response

            else:
                raise Exception("File type not allowed")

        except Exception as e:
            error_message = str(e)  # Get the error message
            return render_template("register.html", message=error_message)

    # If GET request, render registration form
    return render_template("register.html", message="")


if __name__ == '__main__':
    app.run(debug=True, port=4354, host="0.0.0.0")
