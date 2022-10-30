import csv
import io
import json

from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, Product, ProductCategory, Category
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity, verify_jwt_in_request
from sqlalchemy import and_
from decorator import roleCheck
from redis import Redis

app = Flask(__name__)
app.config.from_object(Configuration)
jwt = JWTManager(app)

@app.route("/test", methods = ["GET"])
def test():
    with Redis(host=Configuration.REDIS_HOST) as redis:
        miki = {
            "categories": ["c1", "c2"],
            "name": "kafa",
            "quantity": 15,
            "price": 400
        }
        redis.lpush(Configuration.REDIS_THREADS_LIST, json.dumps(miki))
    return Response("OVER")


@app.route("/update", methods = ["POST"])
@roleCheck(role="manager")
def update():
    updateFile = request.files.get("file", None)
    if updateFile is None:
        return jsonify({"message": "Field file is missing."}), 400
    content = updateFile.stream.read().decode("utf-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)
    products = []
    line = 0
    for row in reader:
        if len(row) != 4:
            return jsonify({"message": f"Incorrect number of values on line {line}."}), 400
        categories = row[0].split("|")
        name = row[1]
        quantity = row[2]
        price = row[3]
        if quantity.isnumeric() == False or int(quantity) <= 0:
            return jsonify({"message": f"Incorrect quantity on line {line}."}), 400
        if price.replace('.','',1).isdigit() == False or float(price) <= 0:
            return jsonify({"message": f"Incorrect price on line {line}."}), 400
        product_info = {
            "categories": categories,
            "name": name,
            "quantity": quantity,
            "price": price
        }
        products.append(product_info)
        line += 1

    with Redis(host = Configuration.REDIS_HOST) as redis:
        for product in products:
            redis.lpush(Configuration.REDIS_THREADS_LIST, json.dumps(product))
    return Response(status = 200)





if __name__ == "__main__":
    database.init_app(app)
    app.run(debug = True, host="0.0.0.0", port = 5001)