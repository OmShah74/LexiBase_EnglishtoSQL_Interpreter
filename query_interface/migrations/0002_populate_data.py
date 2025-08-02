# query_interface/migrations/0002_populate_data.py

from django.db import migrations
from faker import Faker
import random
from datetime import date

def create_sample_data(apps, schema_editor):
    """Creates sample data for the Employee and Product models."""
    Employee = apps.get_model('query_interface', 'Employee')
    Product = apps.get_model('query_interface', 'Product')
    
    # Use Faker to generate realistic data
    fake = Faker()

    # Create 20 employees
    departments = ['Engineering', 'Sales', 'Marketing', 'HR']
    job_titles = ['Software Engineer', 'Sales Representative', 'Marketing Manager', 'HR Specialist', 'Data Analyst']
    for _ in range(20):
        Employee.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            job_title=random.choice(job_titles),
            department=random.choice(departments),
            salary=random.randint(50000, 150000),
            hire_date=fake.date_between(start_date='-5y', end_date='today')
        )
        
    # Create 20 products
    categories = ['Electronics', 'Books', 'Home Goods', 'Clothing']
    for _ in range(20):
        Product.objects.create(
            name=fake.bs().title(),
            category=random.choice(categories),
            stock_quantity=random.randint(0, 100),
            price=round(random.uniform(10.0, 500.0), 2)
        )

class Migration(migrations.Migration):

    dependencies = [
        ('query_interface', '0001_initial'), # Depends on the initial table creation
    ]

    operations = [
        migrations.RunPython(create_sample_data),
    ]