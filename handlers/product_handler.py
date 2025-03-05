import json
import boto3
import decimal
import urllib
import csv
from decimal import Decimal
from models.product import Product
from gateways.dynamodb_gateway import DynamoDB
from gateways.s3_gateway import S3Gateway
from gateways.sqs_gateway import SQSGateway
from helper.helper_func import build_update_expression, validate_update_product, DecimalEncoder, generate_code
import os

#gateway initialization
db_handler = DynamoDB(os.getenv("DB_NAME"))
product_s3 = S3Gateway(os.getenv("PRODUCT_BUCKET_NAME"))
sqs_s3 = S3Gateway(os.getenv("SQS_BUCKET_NAME"))
sqs_client = SQSGateway(os.getenv("SQS_QUEUE_NAME"))



def product_handler(event, context):
    http_method = event["requestContext"]["http"]["method"]
    product_id = event.get("pathParameters", {}).get("product_id", "none")

    if http_method == "GET":
        return get_product(product_id)
    elif http_method == "DELETE":
        return delete_product(product_id)
    elif http_method == "PUT":
        body = json.loads(event["body"], parse_float=Decimal)
        return update_product(product_id, body)
    else:
        return {"statusCode": 405, "body": json.dumps({"message": "Method Not Allowed"})}
        
        
def get_all_products(event, context):
    try:
        response = db_handler.get_all_items()
        
        if response["statusCode"] != 200:
            return response
        
        return {
            "statusCode": 200,
            "body": json.dumps(response, cls=DecimalEncoder)
        }
        
    except Exception as e:
        return {"statusCode": 500, "message": str(e)}
    

def post_product(event, context):
    """Handles posting a new product to DynamoDB and sending a message to SQS."""
    try:
        body = json.loads(event["body"], parse_float=Decimal)
        
        product = Product(
            product_id=body["product_id"],
            product_name=body["product_name"],
            price=body["price"],
            quantity=body["quantity"],
            brand_name=body.get("brand_name", "")
        )
        
        response = db_handler.put_item(product.get_data())
        
        if response["statusCode"] != 200:
            return {response}
        
        print("Notice: Product added successfully!")
        
        sqs_client.send_message(json.dumps(body, cls=DecimalEncoder))
        
        return {
            "statusCode": 200,
            "message": "Product added successfully",
            "body": json.dumps(body, cls=DecimalEncoder)
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"message": str(e)})}
        
def get_product(product_id):
    try:
        response = db_handler.get_item({"product_id": product_id})
        
        if response["statusCode"] != 200:
            return response
        
        return {
            "statusCode": 200,
            "body": json.dumps(response, cls=DecimalEncoder)
        }
        
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"message": str(e)})}
        
def delete_product(product_id):
    try:
        response = db_handler.delete_item({"product_id": product_id})
        
        if response["statusCode"] != 200:
            return response
        
        return {
            "statusCode": 200,
            "body": json.dumps(response, cls=DecimalEncoder)
        }
        
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"message": str(e)})}

def update_product(product_id, body):
    try:
        validate_update_product(product_id, body)
        
        expression_to_update, expression_val = build_update_expression(body)
        
        if expression_to_update:
            expression_to_update = "SET " + ", ".join(expression_to_update)
            
            try:
                response = db_handler.update_item({"product_id": product_id}, expression_to_update, expression_val)
            
                if response["statusCode"] != 200:
                    return response
                
                return {
                    "statusCode": 200,
                    "body": json.dumps(response, cls=DecimalEncoder)
                }
            
            except Exception as e:
                return {"statusCode": 500, "message": str(e)}
        
        return {"statusCode": 400, "body": json.dumps({"message": "No valid fields to update"})}
    
    except ValueError as e:
        return {"statusCode": 500, "body": json.dumps({"message": str(e)})}

def batch_create_products(event, context):
    print("file uploaded trigger")
    print(event)
    
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    localFilename = f'/tmp/for_create.csv'
    
    try:
        product_s3.download_file(key, localFilename)
        
        with open(localFilename, 'r') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                product = Product(
                    product_id=row['product_id'],
                    product_name=row['product_name'],
                    price=Decimal(row['price']),
                    quantity=int(row['quantity']),
                    brand_name=row.get("brand_name", "")
                )
                db_handler.put_item(
                   item=product.get_data()
                )
                print("Notice: products from the csv file successfully added to the products table")
    except ValueError as e:
        print(f"Error: {e}")

def batch_delete_products(event, context):
    print("file uploaded trigger")
    print(event)
    
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    localFilename = f'/tmp/for_create.csv'
    
    try:
        product_s3.download_file(key, localFilename)
        
        with open(localFilename, 'r') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                db_handler.delete_item({"product_id": row['product_id']})
                print("Notice: products from the csv file successfully deleted")
    except ValueError as e:
        print(f"Error: {e}")

def receive_message_from_sqs(event, context):
    print(event)
    fieldnames=["product_id", "product_name", "price", "quantity"]
    file_randomized_prefix = generate_code("pycon_", 8)
    file_name = f'/tmp/product_created_{file_randomized_prefix}.csv'
    object_name = f'product_created_{file_randomized_prefix}.csv'
    
    
    with open(file_name, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        for payload in event["Records"]:
            json_payload = json.loads(payload["body"])
            writer.writerow(json_payload)
    
    response = sqs_s3.upload_file(file_name, object_name)
        
    print("All done!")
    return {}