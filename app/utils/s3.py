import uuid
import boto3
from flask import current_app

def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=current_app.config['AWS_S3_REGION']
    )

def upload_to_s3(file):
    s3 = get_s3_client()
    bucket = current_app.config['AWS_S3_BUCKET']
    region = current_app.config['AWS_S3_REGION']
    filename = f"{uuid.uuid4()}_{file.filename}"

    s3.upload_fileobj(
        file, bucket, filename,
        ExtraArgs={"ContentType": file.content_type}
    )

    return f"https://{bucket}.s3.{region}.amazonaws.com/{filename}"