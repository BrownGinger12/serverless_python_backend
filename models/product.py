import decimal

class Product:
    def __init__(self, product_id, product_name, price, quantity, brand_name=""):
        self.validate_product_id(product_id)
        self.validate_product_name(product_name)
        self.validate_price(price)
        self.validate_quantity(quantity)

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