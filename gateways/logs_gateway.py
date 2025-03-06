import boto3
import time
import json

class CloudWatchLogger:
    def __init__(self, log_group_name, log_stream_name, region="us-east-1"):
        self.client = boto3.client('logs', region_name=region)
        self.log_group_name = log_group_name
        self.log_stream_name = log_stream_name
        self.sequence_token = None  # Stores the latest sequence token

    def send_log(self, message):
        """Sends a log message to CloudWatch."""

        log_event = {
            "logGroupName": self.log_group_name,
            "logStreamName": self.log_stream_name,
            "logEvents": [
                {
                    "timestamp": int(time.time() * 1000),  # Convert time to milliseconds
                    "message": json.dumps(message)  # Convert message to JSON
                }
            ],
        }

        response = self.client.put_log_events(**log_event)
        print(f"Log sent: {response}")