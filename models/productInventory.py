from datetime import datetime
import decimal
import os
from gateways.dynamodb_gateway import DynamoDB
from helper.helper_func import build_update_expression, validate_update_product

db_handler = DynamoDB(os.getenv("DB_INVENTORY_NAME"))

class Product_Inventory:
    def __init__(self, product_id, datetime="", quantity=0, remarks=""):

        self.product_id = product_id
        self.datetime = datetime
        self.quantity = quantity
        self.remarks = remarks
    
    def get_data(self):
        return {
            "product_id": self.product_id,
            "datetime": self.datetime,
            "quantity": self.quantity,
            "remarks": self.remarks
        }
    
    def validate_product_inv(self):
        self.validate_product_id(self.product_id)
        self.validate_datetime(self.datetime)
        self.validate_quantity(self.quantity)
        
    def validate_product_id(self, product_id):
        if not product_id or not isinstance(product_id, str):
            raise ValueError("Product ID cannot be empty and must be a string.")

    def validate_datetime(self, dt):
        try:
            datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")  # Example format: '2025-03-06 14:30:00'
        except ValueError:
            raise ValueError("Invalid datetime format. Use 'YYYY-MM-DD HH:MM:SS'.")

    def validate_quantity(self, quantity):
        if not isinstance(quantity, (int, float)):
            raise ValueError("Quantity must be a number.")
    
    def create(self):
        self.validate_product_inv()
        
        response = db_handler.put_item(self.get_data())
    
        if response["statusCode"] == 200:
            print("Notice: Product successfully added to the invetory!")
        
        return response
    
    def delete(self):
        response = db_handler.delete_item({"product_id": self.product_id})
        
        if response["statusCode"] == 200:
            print("Notice: product deleted successfully")
            
        return response
    
    def get(self):
        response = db_handler.get_item({"product_id": self.product_id})
        
        return response
    
    def update(self, body):
        validate_update_product(self.product_id, body)
        
        expression_to_update, expression_val = build_update_expression(body)
        
        if expression_to_update:
            expression_to_update = "SET " + ", ".join(expression_to_update)
            
            response = db_handler.update_item({"product_id": self.product_id}, expression_to_update, expression_val)
                
            if response["statusCode"] == 200:
                print("Notice: Product updated successfully!")
        
            return response
        
        return {"statusCode": 400, "message": "No valid fields to update"}