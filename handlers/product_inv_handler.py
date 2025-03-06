from models.productInventory import Product_Inventory
from decimal import Decimal
import decimal
import json
from datetime import datetime
from helper.helper_func import DecimalEncoder
import os

import boto3

def get_current_datetime():
    """Returns the current date and time in 'YYYY-MM-DD HH:MM:SS' format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def post_product_inv(event, context):
    try:
        print(event)
        
        
        if 'detail' in event:
            body = event['detail']
            
            product_inv = Product_Inventory(
                product_id=body["product_id"],
                datetime=get_current_datetime(),
                quantity=body["quantity"],
                remarks=body.get("remarks", "")
                )
                
            response = product_inv.create()
            
            print(body)
            print(response)
            return response
            
    except ValueError as e:
        return {"message": e}