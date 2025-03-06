import decimal
import os
import json
from gateways.dynamodb_gateway import DynamoDB
from models.EventBridgeEvent import EventbridgeEvent
from helper.helper_func import build_update_expression, validate_update_product, DecimalEncoder

db_handler = DynamoDB(os.getenv("DB_NAME"))

class Product:
    def __init__(self, product_id, product_name="", price=0.0, quantity=0, brand_name=""):
        self.product_id = product_id
        self.product_name = product_name
        self.brand_name = brand_name
        self.price = price
        self.quantity = quantity

    def get_data(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "brand_name": self.brand_name,
            "price": self.price,
            "quantity": self.quantity
        }
    
    def validate_product(self):
        self.validate_product_id(self.product_id)
        self.validate_product_name(self.product_name)
        self.validate_price(self.price)
        self.validate_quantity(self.quantity)

    # Validation Methods
    def validate_product_id(self, product_id):
        """Checks if product_id is empty."""
        if not isinstance(product_id, str) or not product_id.strip():
            raise ValueError("Product ID must not be empty")

    def validate_product_name(self, product_name):
        """Checks if product_name is empty."""
        if not isinstance(product_name, str) or not product_name.strip():
            raise ValueError("Product name must not be empty")

    def validate_price(self, price):
        """Checks if price is a decimal and non-negative."""
        if not isinstance(price, (int, float, decimal.Decimal)):
            raise ValueError("Price must be a decimal or number")
        if price < 0:
            raise ValueError("Price cannot be negative")

    def validate_quantity(self, quantity):
        """Checks if quantity is a number and non-negative."""
        if not isinstance(quantity, (int, float)):
            raise ValueError("Quantity must be a number")
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
            
    def create(self):
        self.validate_product()
        
        response = db_handler.put_item(self.get_data())
    
        if response["statusCode"] == 200:
            print("Notice: Product added successfully!")
            event = EventbridgeEvent("product_added", json.dumps(self.get_data(), cls=DecimalEncoder))
            event.send()
        
        return response
    
    def delete(self):
        response = db_handler.delete_item({"product_id": self.product_id})
        
        if response["statusCode"] == 200:
            print("Notice: item deleted successfully")
        
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