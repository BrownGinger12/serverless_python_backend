import boto3

class DynamoDB:
    def __init__(self, table_name):
        self.dynamodb = boto3.resource("dynamodb", "us-east-2")
        self.table = self.dynamodb.Table(table_name)
        
        
    def item_exists(self, key):
        """Checks if an item exists in the table."""
        try:
            response = self.table.get_item(Key=key)
            return "Item" in response and response["Item"] is not None  # ✅ Ensures non-empty item
        except Exception as e:
            return {"statusCode": 500, "message": str(e)}

    def put_item(self, item):
        """Inserts a new item only if it does not already exist."""
        key = {"product_id": item["product_id"]}
        if self.item_exists(key):
            return {"statusCode": 400, "message": "Item already exists"}
        
        try:
            self.table.put_item(Item=item)
            return {"statusCode": 200, "message": "Item added successfully", "data": item}
        except Exception as e:
            return {"statusCode": 500, "message": str(e)}

    def get_item(self, key):
        """Fetches an item from the table using its key."""
        try:
            response = self.table.get_item(Key=key)
            if "Item" in response:
                return {"statusCode": 200, "data": response["Item"]}
            return {"statusCode": 404, "message": "Item not found"}
        except Exception as e:
            return {"statusCode": 500, "message": str(e)}

    def get_all_items(self):
        """Fetches all items from the table."""
        try:
            response = self.table.scan()
            return {"statusCode": 200, "data": response.get("Items", [])}
        except Exception as e:
            return {"statusCode": 500, "message": str(e)}

    def update_item(self, key, update_expression, expression_values):
        """Updates an item only if it exists."""
        if not self.item_exists(key):
            return {"statusCode": 404, "message": "Item does not exist"}

        try:
            response = self.table.update_item(
                Key=key,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues="UPDATED_NEW"
            )
            return {"statusCode": 200, "message": "Item updated successfully", "updatedAttributes": response.get("Attributes", {})}
        except Exception as e:
            return {"statusCode": 500, "message": str(e)}

    def delete_item(self, key):
        """Deletes an item only if it exists."""
        if not self.item_exists(key):
            return {"statusCode": 404, "message": "Item does not exist"}

        try:
            self.table.delete_item(Key=key)
            return {"statusCode": 200, "message": "Item deleted successfully"}
        except Exception as e:
            return {"statusCode": 500, "message": str(e)}