import sqlite3

from flask import Flask, request, Response

from Database import RestaurantDB

# instance of flask application
user_app = Flask(__name__)


# home route that returns below text
# when root url is accessed
@user_app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


# Endpoint to create a new guide
@user_app.route('/user', methods=["POST"])
def add_user():
    firstname = request.json['firstname']
    lastname = request.json['lastname']
    phone_number = request.json['phone_number']
    mail = request.json['mail']
    password = request.json['password']

    try:
        db = RestaurantDB()
        db.add_user(firstname, lastname, phone_number, mail, password)
    except sqlite3.Error as er:
        return Response(
            str(er),
            status=400,
        )

    return "Added user to database"


@user_app.route('/user', methods=["GET"])
def login():
    mail = request.json['mail']
    password = request.json['password']
    try:
        db = RestaurantDB()
        user = db.get_user_by_mail(mail)[0]
        if user[5] == password:
            return 'success'
    except sqlite3.Error as er:
        return Response(
            str(er),
            status=400,
        )

    return "failure"


if __name__ == '__main__':
    user_app.run(debug=True, port=8001)
