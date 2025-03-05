import boto3
import botocore.exceptions

class S3Gateway:
    def __init__(self, bucket_name):
        """Initialize the S3 client with a specified bucket and region."""
        self.s3_client = boto3.client("s3", "us-east-2")
        self.bucket_name = bucket_name

    def upload_file(self, file_path, s3_key):
        """Uploads a file to S3."""
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            return {"status": "success", "message": f"File {s3_key} uploaded successfully"}
        except botocore.exceptions.BotoCoreError as e:
            return {"status": "error", "message": str(e)}

    def download_file(self, s3_key, download_path):
        """Downloads a file from S3."""
        try:
            self.s3_client.download_file(self.bucket_name, s3_key, download_path)
            return {"status": "success", "message": f"File {s3_key} downloaded successfully"}
        except botocore.exceptions.BotoCoreError as e:
            return {"status": "error", "message": str(e)}

    def delete_file(self, s3_key):
        """Deletes a file from S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return {"status": "success", "message": f"File {s3_key} deleted successfully"}
        except botocore.exceptions.BotoCoreError as e:
            return {"status": "error", "message": str(e)}