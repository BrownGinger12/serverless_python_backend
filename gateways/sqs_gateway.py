import boto3

class SQSGateway:
    def __init__(self, queue_name, region_name='us-east-2'):
        """Initialize the SQS client with the given queue name."""
        self.sqs = boto3.resource('sqs', region_name=region_name)
        self.queue = self.sqs.get_queue_by_name(QueueName=queue_name)

    def send_message(self, message_body, message_attributes=None):
        """
        Send a message to the SQS queue.
        :param message_body: The content of the message.
        :param message_attributes: Optional attributes for the message.
        :return: Response from SQS
        """
        response = self.queue.send_message(
            MessageBody=message_body
        )
        return response