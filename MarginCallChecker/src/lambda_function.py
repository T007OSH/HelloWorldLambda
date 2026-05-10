import json
import boto3
from strands import Agent
from strands.models.bedrock import BedrockModel


def lambda_handler(event, context):
    s3_client = boto3.client("s3")

    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]

    response = s3_client.get_object(Bucket=bucket, Key=key)
    file_content = response["Body"].read().decode("utf-8")

    model = BedrockModel(
        model_id="us.anthropic.claude-sonnet-4-6-v1",
        region_name="us-east-1",
    )

    agent = Agent(model=model)

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

    result = agent(prompt)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "bucket": bucket,
            "key": key,
            "analysis": str(result),
        }),
    }
