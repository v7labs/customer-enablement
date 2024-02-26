import boto3
import requests

s3 = boto3.client("s3")


def lambda_handler(event, context):
    """lambda_handler(event, context):

    Code that can be run as an AWS Lambda function when a file is uploaded to an S3 bucket.

    Designed to automatically register incoming files to any S3 bucket linked to a V7 team.

    USAGE
    Please follow the guidance in this article: https://docs.v7labs.com/docs/streaming-files-from-aws-s3-into-darwin
    """

    api_key = "ApiKey"
    team_slug = "team-slug"
    dataset_slug = "dataset-slug"
    storage_name = "storage-name"

    storage_key = event["Records"][0]["s3"]["object"]["key"]
    file_name = storage_key.rsplit("/", 1)[-1]

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"ApiKey {api_key}",
    }

    payload = {
        "items": [
            {"path": "/", "storage_key": f"{storage_key}", "name": f"{file_name}"}
        ],
        "dataset_slug": dataset_slug,
        "storage_slug": storage_name,
    }

    response = requests.post(
        f"https://darwin.v7labs.com/api/v2/teams/{team_slug}/items/register_existing",
        json=payload,
        headers=headers,
    )

    print(response.text)
