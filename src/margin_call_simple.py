import json
from strands import Agent
from strands.models.bedrock import BedrockModel


def lambda_handler(event, context):
    question = event.get("question", "Is the sky blue?")

    model = BedrockModel(
        model_id="us.anthropic.claude-sonnet-4-5-20241022-v2:0",
        region_name="us-east-1",
    )

    agent = Agent(model=model)

    prompt = f"""Answer the following question with only "yes" or "no". Do not provide any explanation.

Question: {question}
"""

    result = agent(prompt)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "question": question,
            "answer": str(result),
        }),
    }
