import boto3

class EventbridgeGateway:
    @classmethod
    def put_event(cls, event):
        client = boto3.client('events')

        return client.put_events(Entries=[event])