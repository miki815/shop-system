from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, Product, ProductCategory, Category, Order, OrderProduct
from email.utils import parseaddr
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity, verify_jwt_in_request
from sqlalchemy import and_
from decorator import roleCheck
import json

app = Flask(__name__)
app.config.from_object(Configuration)
app.config['JSON_SORT_KEYS'] = False
jwt = JWTManager(app)

@app.route("/productStatistics", methods = ["GET"])
@roleCheck(role="admin")
def productStatistics():
    orders = Order.query.all()
    products = []
    sold = []
    waiting = []
    for order in orders:
        for product in order.products:
            order_product = OrderProduct.query.filter(and_(OrderProduct.productId == product.id, OrderProduct.orderId == order.id)).first()
            requested = order_product.quantity
            received = order_product.received
            if product in products:
                index = products.index(product)
                sold[index] += requested
                waiting[index] += (requested - received)
            else:
                products.append(product)
                sold.append(requested)
                waiting.append(requested - received)
    statistics = []
    for p,s,w in zip(products, sold, waiting):
        statistic = {
            "name": p.name,
            "sold": s,
            "waiting": w
        }
        statistics.append(statistic)
        sorted_statistics = sorted(statistics, key = lambda d: d['name'])
    return jsonify({"statistics": sorted_statistics})


@app.route("/categoryStatistics", methods = ["GET"])
@roleCheck(role="admin")
def categoryStatistics():
    orders = Order.query.all()
    categories = Category.query.all()
    categories_name = []
    categories_score = []
    for c in categories:
        category_score = {
            "name": c.name,
            "score": 0
        }
        categories_score.append(category_score)
    for order in orders:
        for product in order.products:
            order_product = OrderProduct.query.filter(and_(OrderProduct.productId == product.id, OrderProduct.orderId == order.id)).first()
            quantity = order_product.quantity
            for category in product.categories:
                for cat_score in categories_score:
                    if cat_score["name"] == category.name:
                        cat_score["score"] += quantity
                        break
    sorted_statistics = sorted(categories_score, key=lambda d: d['score'], reverse=True)
    for sorted_stat in sorted_statistics:
        categories_name.append(sorted_stat["name"])
    return jsonify({"statistics": categories_name})




if __name__ == "__main__":
    database.init_app(app)
    app.run(debug = True, host="0.0.0.0", port = 5003)