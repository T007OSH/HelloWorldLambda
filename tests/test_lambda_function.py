import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lambda_function import lambda_handler


def test_lambda_handler_returns_200():
    response = lambda_handler({}, None)
    assert response["statusCode"] == 200


def test_lambda_handler_returns_hello_world_message():
    response = lambda_handler({}, None)
    body = json.loads(response["body"])
    assert body["message"] == "Hello, World!"
