import datetime

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

@app.route("/search", methods = ["GET"])
@roleCheck(role="customer")
def search():
    my_name = request.args.get("name", "")
    my_category = request.args.get("category", "")
    my_categories = []
    my_products = []
    categories = Category.query.filter(Category.name.like(f"%{my_category}%"))
    products = Product.query.filter(Product.name.like(f"%{my_name}%"))
    for category in categories:
        cProducts = category.products
        for p in cProducts:
            if my_name in p.name:
                my_categories.append(category.name)
                break
    for product in products:
        pCategories = product.categories
        success = 0
        if not my_category:
            success = 1
        for c in pCategories:
            if my_category in c.name:
                success = 1
                break
        if success == 1:
            allCat = []
            for cat in product.categories:
                allCat.append(cat.name)
            prod = {
                "categories": allCat,
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": product.quantity
            }
            my_products.append(prod)

    return jsonify({"categories": my_categories, "products": my_products})


@app.route("/order", methods = ["POST"])
@roleCheck(role="customer")
def order():
    if request.json is None:
        return jsonify({"message": "Field requests is missing."}), 400
    requests = request.json.get("requests", "")
    if len(requests) == 0:
        return jsonify({"message": "Field requests is missing."}), 400
    line = 0
    products = []
    quantities = []
    for product_info in requests:
        if not "id" in product_info:
            return jsonify({"message": f"Product id is missing for request number {line}."}), 400
        if not "quantity" in product_info:
            return jsonify({"message": f"Product quantity is missing for request number {line}."}), 400
        if type(product_info["id"]) != int or product_info["id"] <= 0:
            return jsonify({"message": f"Invalid product id for request number {line}."}), 400
        if type(product_info["quantity"]) != int or product_info["quantity"] <= 0:
            return jsonify({"message": f"Invalid product quantity for request number {line}."}), 400
        product = Product.query.filter(Product.id==product_info["id"]).first()
        if not product:
            return jsonify({"message": f"Invalid product for request number {line}."}), 400
        products.append(product)
        quantities.append(product_info["quantity"])
        line += 1
    order = Order(orderTime = datetime.datetime.now())
    database.session.add(order)
    database.session.commit()
    price = float(0)
    satisfies = 1
    for (product, quantity) in zip(products, quantities):
        price += product.price * quantity
        received = 0
        if product.quantity >= quantity:
            product.quantity -= quantity
            received = quantity
        else:
            received = product.quantity
            product.quantity = 0
            satisfies = 0
        order_product = OrderProduct(quantity = quantity, orderId = order.id, productId = product.id, received=received, price=product.price)
        database.session.add(order_product)
        database.session.commit()
    verify_jwt_in_request()
    claims = get_jwt()
    customer_id = claims["id"]
    order.customerId = customer_id
    order.price = price
  #  database.session.add(order)
    order.isWaiting = True if satisfies == 0 else False
    database.session.commit()
    return jsonify({"id": order.id})


@app.route("/status", methods = ["GET"])
@roleCheck(role="customer")
def status():
    verify_jwt_in_request()
    claims = get_jwt()
    customer_id = claims["id"]
    orders = Order.query.filter(Order.customerId == customer_id).all()
    my_orders = []
    for order in orders:
        order_products = []
        for product in order.products:
            product_categories = []
            for cat in product.categories:
                product_categories.append(cat.name)
            orderProduct = OrderProduct.query.filter(and_(OrderProduct.orderId==order.id,OrderProduct.productId==product.id)).first()
            prod = {
                "categories": product_categories,
                "name": product.name,
                "price": orderProduct.price,
                "received": orderProduct.received,
                "requested": orderProduct.quantity
            }
            order_products.append(prod)
        my_order = {
            "products": order_products,
            "price": order.price,
            "status": "PENDING" if order.isWaiting == True else "COMPLETE",
            "timestamp": order.orderTime.isoformat()
        }
        my_orders.append(my_order)
    return jsonify({"orders": my_orders})


if __name__ == "__main__":
    database.init_app(app)
    app.run(debug = True, host="0.0.0.0", port = 5000)
