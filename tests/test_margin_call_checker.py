import json
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def make_s3_event(bucket, key):
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": bucket},
                    "object": {"key": key},
                }
            }
        ]
    }


@patch("margin_call_checker.Agent")
@patch("margin_call_checker.BedrockModel")
@patch("margin_call_checker.boto3")
def test_margin_call_detected(mock_boto3, mock_bedrock_model, mock_agent_class):
    mock_s3 = MagicMock()
    mock_boto3.client.return_value = mock_s3
    mock_s3.get_object.return_value = {
        "Body": MagicMock(read=MagicMock(return_value=b"This is a margin call from Counterparty ABC dated 2025-01-15 for amount 5000000"))
    }

    mock_agent_instance = MagicMock()
    mock_agent_class.return_value = mock_agent_instance
    mock_agent_instance.return_value = '{"is_margin_call": true, "date": "2025-01-15", "counterparty": "ABC", "amount": "5000000"}'

    from margin_call_checker import lambda_handler

    event = make_s3_event("bkt-doc-src-margin-call", "test-file.txt")
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["bucket"] == "bkt-doc-src-margin-call"
    assert body["key"] == "test-file.txt"


@patch("margin_call_checker.Agent")
@patch("margin_call_checker.BedrockModel")
@patch("margin_call_checker.boto3")
def test_not_a_margin_call(mock_boto3, mock_bedrock_model, mock_agent_class):
    mock_s3 = MagicMock()
    mock_boto3.client.return_value = mock_s3
    mock_s3.get_object.return_value = {
        "Body": MagicMock(read=MagicMock(return_value=b"This is a regular trade confirmation document"))
    }

    mock_agent_instance = MagicMock()
    mock_agent_class.return_value = mock_agent_instance
    mock_agent_instance.return_value = '{"is_margin_call": false}'

    from margin_call_checker import lambda_handler

    event = make_s3_event("bkt-doc-src-margin-call", "regular-doc.txt")
    response = lambda_handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["bucket"] == "bkt-doc-src-margin-call"
