from datetime import timedelta
import os

databaseUrl = os.environ["DATABASE_URL"]
redisUrl = os.environ["REDIS_URL"]

class Configuration():
  #  SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost/shopDatabase"
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/shop"
    REDIS_HOST = redisUrl
    REDIS_THREADS_LIST = "products"
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours = 1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days = 30)