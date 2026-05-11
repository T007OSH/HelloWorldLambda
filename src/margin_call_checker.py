import json
import boto3
from strands import Agent
from strands.models.bedrock import BedrockModel


def lambda_handler(event, context):
    print("Starting margin_call_checker lambda_handler")

    print("Creating S3 client")
    s3_client = boto3.client("s3")

    print("Extracting bucket and key from event")
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]
    print(f"Bucket: {bucket}, Key: {key}")

    print("Fetching object from S3")
    response = s3_client.get_object(Bucket=bucket, Key=key)

    print("Reading file content")
    file_content = response["Body"].read().decode("utf-8")
    print(f"File content length: {len(file_content)}")

    print("Creating BedrockModel")
    model = BedrockModel(
        model_id="us.anthropic.claude-sonnet-4-6-v1",
        region_name="us-east-1",
    )

    print("Creating Agent")
    agent = Agent(model=model)

    print("Building prompt")
    prompt = f"""Analyze the following document content and determine if it is a margin call.

Rules:
- If the content contains the words "margin call" then it IS a margin call. Extract the margin call details: date, counterparty, and amount.
- If the content does NOT contain the words "margin call" then it is NOT a margin call.

Document content:
{file_content}

Respond in JSON format:
- If it is a margin call: {{"is_margin_call": true, "date": "<date>", "counterparty": "<counterparty>", "amount": "<amount>"}}
- If it is not a margin call: {{"is_margin_call": false}}
"""

    print("Invoking agent with prompt")
    result = agent(prompt)
    print(f"Agent result: {result}")

    print("Building response")
    response_body = {
        "statusCode": 200,
        "body": json.dumps({
            "bucket": bucket,
            "key": key,
            "analysis": str(result),
        }),
    }

    print(f"Returning response: {response_body}")
    return response_body
