import boto3
from botocore.config import Config

from app.config import settings

client = boto3.client(
    "s3",
    endpoint_url=settings.r2_endpoint,
    aws_access_key_id=settings.r2_access_key_id,
    aws_secret_access_key=settings.r2_secret_access_key,
    region_name="auto",
    config=Config(
        signature_version="s3v4",
        request_checksum_calculation="when_required",
        response_checksum_validation="when_required",
    ),
)


# test if i can contact my R2 bucket
print(settings.r2_bucket)
response = client.list_objects_v2(Bucket=settings.r2_bucket)
n = response["KeyCount"]
print(f"OK, {n} objets")
