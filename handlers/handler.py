import json
import boto3
from decimal import Decimal
import urllib
import csv
import codecs
import string
import random

class DecimalEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Decimal):
      return str(obj)
    return json.JSONEncoder.default(self, obj)

def check_if_product_exist(product_id, table_name):
    db = boto3.resource("dynamodb", "us-east-2")
    table = db.Table(table_name)
    data = table.get_item(Key={"product_id": product_id})
    item = data.get("Item")
    
    if item:
        return {"product": item, "status": True}
    
    return {"product": {}, "status": False}
    
def hello(event, context):
    body = {
        "message": "Go Serverless v4.0! Your function executed successfully!",
    }
    
    print(f"This print statement is for debugging purposes only {event}")

    response = {"statusCode": 200, "body": json.dumps(body)}

    return response
    
def get_all_products(event, context):
    body = {
        "message": "Im getting all the products",
        "event": event
    }
    
    table_name = "products-miles"

    db = boto3.resource("dynamodb", "us-east-2")
    table = db.Table(table_name)
    
    data = table.scan().get('Items')
    
    return {"response": 200, "message": body["message"], "body": json.dumps(data, cls=DecimalEncoder)}

def post_product(event, context):
    body = json.loads(event["body"], parse_float=Decimal)
    
    table_name = "products-miles"

    db = boto3.resource("dynamodb", "us-east-2")
    table = db.Table(table_name)
    
    table.put_item(Item=body)
    
    sqs = boto3.resource('sqs', region_name='us-east-2')
    queue = sqs.get_queue_by_name(QueueName='python-miles-queue')
    
    response = queue.send_message(MessageBody=json.dumps(body, cls=DecimalEncoder))
    
    print("Product created")
    
    return {"response": 200, "message": "product added", "body": json.dumps(body, cls=DecimalEncoder)}

def get_product(event, context):
    product = event.get("pathParameters", {}).get("product_id", "none")
    
    table_name = "products-miles"
    
    print(f"product id is {product}")
    
    db = boto3.resource("dynamodb", "us-east-2")
    table = db.Table(table_name)
    data = table.get_item(Key={"product_id": product})  
    item = data.get("Item")
    
    
    if item:
        return {"response": 200, "product": json.dumps(item, cls=DecimalEncoder)}
    
    return {"response": 200, "message": "product does not exist"}


def delete_product(event, context):
    product = event.get("pathParameters", {}).get("product_id", "none")
    
    table_name = "products-miles"
    
    print(f"product id is {product}")
    
    db = boto3.resource("dynamodb", "us-east-2")
    table = db.Table(table_name)
    data = table.get_item(Key={"product_id": product})
    item = data.get("Item")
    
    if item:
        delete = table.delete_item(Key={"product_id": product})
        return {"response": 200, "message": "product deleted successfully"}
    
    return {"response": 200, "message": "product does not exist"}
    
def update_product(event, context):
    product = event.get("pathParameters", {}).get("product_id", "none")
    body = json.loads(event["body"], parse_float=Decimal)
    
    table_name = "products-miles"
    
    print(f"product id is {product}")
    
    db = boto3.resource("dynamodb", "us-east-2")
    table = db.Table(table_name)
    data = table.get_item(Key={"product_id": product})
    item = data.get("Item")
    
    if item:
        expression_to_update = []
        expression_val = {}
        
        product_name = body.get("product_name")
        brand_name = body.get("brand_name")
        price = body.get("price")
        quantity = body.get("quantity")
        
        if product_name:
            expression_to_update.append("product_name = :val1")
            expression_val[":val1"] = product_name
        if brand_name:
            expression_to_update.append("brand_name = :val2")
            expression_val[":val2"] = brand_name
        if price is not None:
            expression_to_update.append("price = :val3")
            expression_val[":val3"] = price
        if quantity is not None:
            expression_to_update.append("quantity = :val4")
            expression_val[":val4"] = quantity
        
        if expression_to_update:
            expression_to_update = "SET " + ", ".join(expression_to_update)
            update = table.update_item(Key={"product_id": product}, UpdateExpression=expression_to_update, ExpressionAttributeValues=expression_val)
            return {"response": 200, "message": "product updated", "product": json.dumps(update, cls=DecimalEncoder)}
            
        return {"response": 200, "message": "failed to update product", "product": json.dumps({})}
    
    return {"response": 200, "message": "failed to update product, product does not exist"}

def batch_create_products(event, context):
    print("file uploaded trigger")
    print(event)
    
    print("Extract file location from event payload")
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    localFilename = f'/tmp/for_create.csv'
    s3_client = boto3.client('s3', region_name='us-east-2')
    
    print(f"bucket: {bucket} event: {event} file: {localFilename}")
    print("downloaded file to /tmp folder")
    s3_client.download_file(bucket, key, localFilename)
    
    
    table_name = "products-miles"
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table(table_name)
    
    print("reading CSV file and looping it over...")
    
    with open(localFilename, 'r') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            table.put_item(
               Item={
                   "product_id": row['product_id'],
                   "product_name": row['product_name'],
                   "price": Decimal(row['price']),
                   "quantity": int(row['quantity'])
               }
            )
    
    print("All done!")
    return {}

def batch_delete_products(event, context):
    print("file uploaded trigger")
    print(event)
    
    print("Extract file location from event payload")
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    localFilename = f'/tmp/for_delete.csv'
    s3_client = boto3.client('s3', region_name='us-east-2')
    
    print(f"bucket: {bucket} event: {event} file: {localFilename}")
    print("downloaded file to /tmp folder")
    s3_client.download_file(bucket, key, localFilename)
    
    
    table_name = "products-miles"
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table(table_name)
    
    with open(localFilename, 'r') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            print(row)
            table.delete_item(
               Key={"product_id": row['product_id']}
            )
    
    print("All done!")
    return {}

def generate_code(prefix, string_length):
  letters = string.ascii_uppercase
  return prefix + ''.join(random.choice(letters) for i in range(string_length))
  

def receive_message_from_sqs(event, context):
    print(event)
    bucket_name = "miles-queue-bucket"
    s3 = boto3.client("s3")
    
    fieldnames=["product_id", "product_name", "price", "quantity"]
    file_randomized_prefix = generate_code("pycon_", 8)
    file_name = f'/tmp/product_created_{file_randomized_prefix}.csv'
    object_name = f'product_created_{file_randomized_prefix}.csv'
    
    
    with open(file_name, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        for payload in event["Records"]:
            json_payload = json.loads(payload["body"])
            writer.writerow(json_payload)
    
    response = s3.upload_file(file_name, bucket_name, object_name)
        
    print("All done!")
    return {}