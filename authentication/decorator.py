from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import Flask, request, Response, jsonify


def roleCheck(role):
    def innerRole(function):
        @wraps(function)
        def decorator(*arguments, **keywordArguments):
            auth = request.headers.get("Authorization", "")
            if len(auth) == 0:
                return jsonify({"msg": "Missing Authorization Header"}), 401
            verify_jwt_in_request()
            claims = get_jwt()
            if "role" in claims and role == claims["role"]:
                return function(*arguments, **keywordArguments)
            else:
                return jsonify({"msg": "Missing Authorization Header"}), 401
        return decorator
    return innerRole