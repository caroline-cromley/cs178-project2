import csv
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# config
NUM_RECORDS = 500
OUTPUT_FILE = 'sample_output.csv'

REGIONS = ["Midwest", "Northeast", "South", "West"]
CATEGORIES = ["Electronics", "Apparel", "Home Goods", "Sporting Goods", "Office Supplies"]
STATUSES = ["completed", "pending", "refunded", "COMPLETED", "Pending", None]   #intentional dirty values
 
def random_date(start_year=2023, end_year=2024):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))
 
def generate_record():
    quantity = random.randint(1, 20)
    unit_price = round(random.uniform(5.00, 299.99), 2)
    total = round(quantity * unit_price, 2)
 
    # intentionally introduce dirty data for Glue to clean
    dirty_quantity = quantity if random.random() > 0.05 else None       # 5% missing quantity
    dirty_total = total if random.random() > 0.05 else ""               # 5% missing total
    dirty_status = random.choice(STATUSES)                              # inconsistent casing + nulls
    dirty_price = unit_price if random.random() > 0.03 else -unit_price # 3% negative prices
 
    return {
        "order_id": fake.uuid4(),
        "customer_name": fake.name(),
        "customer_email": fake.email(),
        "region": random.choice(REGIONS),
        "category": random.choice(CATEGORIES),
        "product_name": fake.catch_phrase(),
        "quantity": dirty_quantity,
        "unit_price": dirty_price,
        "order_total": dirty_total,
        "order_date": random_date().strftime("%Y-%m-%d"),
        "status": dirty_status,
    }
 
def main():
    records = [generate_record() for _ in range(NUM_RECORDS)]
    fieldnames = records[0].keys()
 
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
 
    print(f"Generated {NUM_RECORDS} records -> {OUTPUT_FILE}")
 
if __name__ == "__main__":
    main()
 