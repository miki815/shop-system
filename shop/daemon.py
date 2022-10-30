import csv
import io
import json
import time
import threading

from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, Product, ProductCategory, Category, Order, OrderProduct
from sqlalchemy import and_
from redis import Redis


app = Flask(__name__)
app.config.from_object(Configuration)


def deamon_thread():
    with Redis(host=Configuration.REDIS_HOST) as redis:
        while True:
            while redis.llen(Configuration.REDIS_THREADS_LIST) != 0:
                with app.app_context():
                    product_info = json.loads(redis.rpop(Configuration.REDIS_THREADS_LIST))
                    categories = product_info["categories"]
                    name = product_info["name"]
                    quantity = int(product_info["quantity"])
                    price = float(product_info["price"])
                    product = Product.query.filter(Product.name == name).first()
                    valid = 1
                    if product is None:
                        product = Product(name=name,quantity=quantity,price=price)
                        database.session.add(product)
                        database.session.commit()
                        for category in categories:
                            category_exist = Category.query.filter(Category.name == category).first()
                            if category_exist is None:
                                category_exist = Category(name=category)
                                database.session.add(category_exist)
                                database.session.commit()
                            product_category = ProductCategory(productId=product.id,categoryId=category_exist.id)
                            database.session.add(product_category)
                            database.session.commit()
                    else:
                        if len(categories) != len(product.categories):
                            valid = 0
                        else:
                            prod_cat_names = []
                            for prod_category in product.categories:
                                    prod_cat_names.append(prod_category.name)
                            for category in categories:
                                if category not in prod_cat_names:
                                    valid = 0
                                    break
                        if valid:
                            product.price = (product.quantity * product.price + quantity * price) / (product.quantity + quantity)
                            product.quantity += quantity
                            database.session.commit()
                            orders_waiting = OrderProduct.query.filter(OrderProduct.productId==product.id)
                            # update waiting orders
                            for order_wait in orders_waiting:
                                if product.quantity >= (order_wait.quantity - order_wait.received):
                                    product.quantity = product.quantity - order_wait.quantity + order_wait.received
                                    order_wait.received = order_wait.quantity
                                    database.session.commit()
                                    # check if it is last for this order
                                    allForThisOrder = OrderProduct.query.filter(OrderProduct.orderId == order_wait.orderId)
                                    isFinish = 1
                                    for orderP in allForThisOrder:
                                        if orderP.quantity != orderP.received:
                                            isFinish = 0
                                            break
                                    if isFinish == 1:
                                        my_order = Order.query.filter(Order.id==order_wait.orderId).first()
                                        my_order.isWaiting = False
                                        database.session.commit()
                                else:
                                    order_wait.received += product.quantity
                                    product.quantity = 0
                                    database.session.commit()
                                    break


thread = threading.Thread(name="deamon_thread", target=deamon_thread)
thread.setDaemon(True)
thread.start()


if __name__ == "__main__":
    database.init_app(app)
    app.run(debug = True, host="0.0.0.0", port = 5004)



