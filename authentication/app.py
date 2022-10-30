from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, User
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity, verify_jwt_in_request
from sqlalchemy import and_
from decorator import roleCheck
import re

app = Flask(__name__)
app.config.from_object(Configuration)
jwt = JWTManager(app)

@app.route("/hello", methods = ["GET"])
def helloWorld():
    return Response("Hello World")


@app.route("/register", methods = ["POST"])
def register():
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    isCustomer = request.json.get("isCustomer", None)

    if len(forename) == 0:
        return jsonify({"message": "Field forename is missing."}), 400
    if len(surname) == 0:
        return jsonify({"message": "Field surname is missing."}), 400
    if len(email) == 0:
        return jsonify({"message": "Field email is missing."}), 400
    if len(password) == 0:
        return jsonify({"message": "Field password is missing."}), 400
    if isCustomer is None:
        return jsonify({"message": "Field isCustomer is missing."}), 400
    regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
    if not re.search(regex, email):
        return jsonify({"message": "Invalid email."}), 400
    small = False
    big = False
    num = False
    for p in password:
        if p.islower():
            small = True
        elif p.isupper():
            big = True
        elif p.isdigit():
            num = True
    if len(password) < 8 or small == False or big == False or num == False:
        return jsonify({"message": "Invalid password."}), 400
    user = User.query.filter(User.email == email).first()
    if user:
        return jsonify({"message": "Email already exists."}), 400
    role = "manager" if isCustomer == False else "customer"
    user = User(email = email, password = password, forename = forename, surname = surname, role = role)
    database.session.add(user)
    database.session.commit()
    return Response(status=200)


@app.route("/login", methods = ["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    if len(email) == 0:
        return jsonify({"message": "Field email is missing."}), 400
    if len(password) == 0:
        return jsonify({"message": "Field password is missing."}), 400
    regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
    if not re.search(regex, email):
        return jsonify({"message": "Invalid email."}), 400

    user = User.query.filter(and_(User.email == email, User.password == password)).first()
    if not user:
        return jsonify({"message": "Invalid credentials."}), 400

    additionalClaims = {
        "id": user.id,
        "role": user.role,
        "forename": user.forename,
        "surname": user.surname
    }

    accessToken = create_access_token(identity = user.email, additional_claims=additionalClaims)
    refreshToken = create_refresh_token(identity = user.email, additional_claims=additionalClaims)
    return jsonify({"accessToken": accessToken, "refreshToken": refreshToken})


@app.route("/refresh", methods = ["POST"])
def refresh():
    auth = request.headers.get("Authorization", "")
    if len(auth) == 0:
        return jsonify({"msg": "Missing Authorization Header"}), 401
    verify_jwt_in_request(refresh=True)
    identity = get_jwt_identity()
    refreshClaims = get_jwt()
    claims = {
        "id": refreshClaims["id"],
        "role": refreshClaims["role"],
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"]
    }
    accessToken = create_access_token(identity = identity, additional_claims=claims)
    return jsonify({"accessToken": accessToken})



@app.route("/delete", methods = ["POST"])
@roleCheck(role="admin")
def delete():
    email = request.json.get("email", "")
    if len(email) == 0:
        return jsonify({"message": "Field email is missing."}), 400
    regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
    if not re.search(regex, email):
        return jsonify({"message": "Invalid email."}), 400
    user = User.query.filter(User.email == email).first()
    if not user:
        return jsonify({"message": "Unknown user."}), 400
    database.session.delete(user)
    database.session.commit()
    return Response(status=200)





if __name__ == "__main__":
    database.init_app(app)
    app.run(debug = True, host="0.0.0.0", port=5002)


