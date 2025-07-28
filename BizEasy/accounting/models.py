from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username



class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class ProductSubcategory(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(ProductSubcategory, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# ✅ This is the missing model
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{self.get_type_display()} Transaction - ₹{self.amount:.2f} by {self.user.username} on {self.date.strftime('%d-%m-%Y')}"

class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.FloatField()

    def __str__(self):
        return "{} x {}".format(self.product.name, self.quantity)

class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    items = models.TextField()  # JSON string
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)


# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     business_name = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"{self.user.username} - {self.business_name}"
#
# class ProductCategory(models.Model):
#     name = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.name
#
# class ProductSubcategory(models.Model):
#     category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"{self.category.name} - {self.name}"
#
# class Product(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#     category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
#     subcategory = models.ForeignKey(ProductSubcategory, on_delete=models.CASCADE)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     quantity = models.IntegerField()
#     description = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return self.name
#
# class Transaction(models.Model):
#     TRANSACTION_TYPES = (
#         ('income', 'Income'),
#         ('expense', 'Expense'),
#     )
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
#     subcategory = models.ForeignKey(ProductSubcategory, on_delete=models.CASCADE)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     date = models.DateField()
#     note = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"{self.type} - {self.amount}"
#
# class Invoice(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     customer_name = models.CharField(max_length=100)
#     items = models.JSONField()
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     tax_percent = models.DecimalField(max_digits=5, decimal_places=2)
#     date = models.DateField()
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"Invoice for {self.customer_name}"

# class Transaction(models.Model):
#     TRANSACTION_TYPES = (("income", "Income"), ("expense", "Expense"))
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
#     subcategory = models.ForeignKey(ProductSubcategory, on_delete=models.CASCADE)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     date = models.DateField()
#     note = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)