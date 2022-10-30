from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

class ProductCategory(database.Model):
    __tablename__ = "productcategory"
    id = database.Column(database.Integer, primary_key=True)
    productId = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False)
    categoryId = database.Column(database.Integer, database.ForeignKey("categories.id"), nullable=False)


class OrderProduct(database.Model):
    __tablename__ = "orderproduct"
    id = database.Column(database.Integer, primary_key=True)
    quantity = database.Column(database.Integer)
    received = database.Column(database.Integer)
    price = database.Column(database.Float)
    orderId = database.Column(database.Integer, database.ForeignKey("orders.id"), nullable=False)
    productId = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False)


class Product(database.Model):
    __tablename__ = "products"
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable = False, unique = True)
    price = database.Column(database.Float)
    quantity = database.Column(database.Integer)

    categories = database.relationship("Category", secondary=ProductCategory.__table__, back_populates="products")
    orders = database.relationship("Order", secondary=OrderProduct.__table__, back_populates="products")


class Category(database.Model):
    __tablename__ = "categories"
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable = False, unique = True)

    products = database.relationship("Product", secondary=ProductCategory.__table__, back_populates="categories")


class Order(database.Model):
    __tablename__ = "orders"
    id = database.Column(database.Integer, primary_key=True)
    price = database.Column(database.Float)
    isWaiting = database.Column(database.Boolean)
    orderTime = database.Column(database.DateTime)
    customerId = database.Column(database.Integer)

    products = database.relationship("Product", secondary=OrderProduct.__table__, back_populates="orders")
