import csv
import random
from datetime import datetime, timedelta

random.seed(42)

REGIONS = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East & Africa"]
COUNTRIES = {
    "North America": ["United States", "Canada", "Mexico"],
    "Europe": ["Germany", "United Kingdom", "France", "Netherlands", "Spain"],
    "Asia Pacific": ["Japan", "Australia", "South Korea", "India", "Singapore"],
    "Latin America": ["Brazil", "Argentina", "Colombia"],
    "Middle East & Africa": ["UAE", "South Africa", "Saudi Arabia"],
}
CATEGORIES = ["Electronics", "Furniture", "Office Supplies", "Clothing", "Food & Beverage"]
SUB_CATEGORIES = {
    "Electronics": ["Laptops", "Smartphones", "Tablets", "Monitors", "Accessories"],
    "Furniture": ["Desks", "Chairs", "Shelving", "Tables", "Cabinets"],
    "Office Supplies": ["Paper", "Pens", "Binders", "Labels", "Envelopes"],
    "Clothing": ["Shirts", "Pants", "Jackets", "Shoes", "Accessories"],
    "Food & Beverage": ["Snacks", "Beverages", "Coffee", "Tea", "Catering"],
}
SEGMENTS = ["Consumer", "Corporate", "Small Business", "Enterprise", "Government"]
CHANNELS = ["Online", "Retail Store", "Wholesale", "Distributor"]
PAYMENT_METHODS = ["Credit Card", "Bank Transfer", "PayPal", "Invoice", "Cash"]

PRODUCTS = {}
product_id = 1000
for cat, subs in SUB_CATEGORIES.items():
    for sub in subs:
        for i in range(3):
            pid = f"PRD-{product_id}"
            name = f"{sub} {'Pro' if i == 0 else 'Standard' if i == 1 else 'Basic'}"
            base_price = round(random.uniform(10, 2000), 2)
            cost = round(base_price * random.uniform(0.35, 0.75), 2)
            PRODUCTS[pid] = {
                "name": name, "category": cat, "sub_category": sub,
                "unit_price": base_price, "unit_cost": cost
            }
            product_id += 1

CUSTOMERS = []
first_names = ["James", "Maria", "Robert", "Sarah", "Michael", "Emma", "David", "Lisa",
               "Carlos", "Yuki", "Hans", "Fatima", "Raj", "Chen", "Ahmed"]
last_names = ["Smith", "Garcia", "Mueller", "Tanaka", "Kim", "Singh", "Chen",
              "Johnson", "Williams", "Brown", "Wilson", "Martinez", "Anderson"]

for i in range(200):
    region = random.choice(REGIONS)
    country = random.choice(COUNTRIES[region])
    CUSTOMERS.append({
        "customer_id": f"CUST-{5000 + i}",
        "name": f"{random.choice(first_names)} {random.choice(last_names)}",
        "segment": random.choice(SEGMENTS),
        "region": region,
        "country": country,
    })

SALES_REPS = []
rep_names = ["Alice Thompson", "Bob Martinez", "Carol Zhang", "Daniel Kim", "Eva Schmidt",
             "Frank Wilson", "Grace Lee", "Henry Brown", "Iris Patel", "Jack Davis"]
for i, name in enumerate(rep_names):
    SALES_REPS.append({
        "rep_id": f"REP-{100 + i}",
        "rep_name": name,
        "region": REGIONS[i % len(REGIONS)],
    })

# --- Generate Dimension CSVs ---
with open("C:/Users/PC/azure-data-portfolio/data/dim_products.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["product_id", "product_name", "category", "sub_category", "unit_price", "unit_cost"])
    for pid, p in PRODUCTS.items():
        w.writerow([pid, p["name"], p["category"], p["sub_category"], p["unit_price"], p["unit_cost"]])

with open("C:/Users/PC/azure-data-portfolio/data/dim_customers.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["customer_id", "customer_name", "segment", "region", "country"])
    for c in CUSTOMERS:
        w.writerow([c["customer_id"], c["name"], c["segment"], c["region"], c["country"]])

with open("C:/Users/PC/azure-data-portfolio/data/dim_sales_reps.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["rep_id", "rep_name", "region"])
    for r in SALES_REPS:
        w.writerow([r["rep_id"], r["rep_name"], r["region"]])

with open("C:/Users/PC/azure-data-portfolio/data/dim_date.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["date_key", "full_date", "year", "quarter", "month", "month_name", "day_of_week", "is_weekend", "fiscal_year", "fiscal_quarter"])
    start = datetime(2023, 1, 1)
    for i in range(912):  # 2023-01-01 to 2025-06-30
        d = start + timedelta(days=i)
        q = (d.month - 1) // 3 + 1
        fy = d.year if d.month >= 7 else d.year - 1
        fq = ((d.month - 7) % 12) // 3 + 1
        w.writerow([
            d.strftime("%Y%m%d"), d.strftime("%Y-%m-%d"), d.year, f"Q{q}",
            d.month, d.strftime("%B"), d.strftime("%A"),
            1 if d.weekday() >= 5 else 0, f"FY{fy}", f"FQ{fq}"
        ])

# --- Generate Fact Table ---
with open("C:/Users/PC/azure-data-portfolio/data/fact_sales.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["order_id", "order_date", "ship_date", "customer_id", "product_id",
                "rep_id", "channel", "payment_method", "quantity", "unit_price",
                "discount_pct", "total_amount", "cost_amount", "profit"])

    order_id = 10000
    start = datetime(2023, 1, 1)
    end = datetime(2025, 6, 30)
    current = start

    while current <= end:
        daily_orders = random.randint(5, 25)
        month = current.month
        if month in [11, 12]:  # holiday season boost
            daily_orders = int(daily_orders * 1.6)
        if current.weekday() >= 5:  # weekend dip
            daily_orders = int(daily_orders * 0.6)

        for _ in range(daily_orders):
            customer = random.choice(CUSTOMERS)
            pid = random.choice(list(PRODUCTS.keys()))
            product = PRODUCTS[pid]

            matching_reps = [r for r in SALES_REPS if r["region"] == customer["region"]]
            rep = random.choice(matching_reps) if matching_reps else random.choice(SALES_REPS)

            qty = random.choices([1, 2, 3, 5, 10, 20, 50], weights=[30, 25, 15, 12, 10, 5, 3])[0]
            discount = random.choices([0, 0.05, 0.10, 0.15, 0.20, 0.25], weights=[40, 20, 15, 12, 8, 5])[0]
            ship_days = random.randint(1, 14)
            ship_date = current + timedelta(days=ship_days)

            total = round(qty * product["unit_price"] * (1 - discount), 2)
            cost = round(qty * product["unit_cost"], 2)
            profit = round(total - cost, 2)

            w.writerow([
                f"ORD-{order_id}", current.strftime("%Y-%m-%d"), ship_date.strftime("%Y-%m-%d"),
                customer["customer_id"], pid, rep["rep_id"],
                random.choice(CHANNELS), random.choice(PAYMENT_METHODS),
                qty, product["unit_price"], discount, total, cost, profit
            ])
            order_id += 1

        current += timedelta(days=1)

# --- Generate Inventory/Returns Data ---
with open("C:/Users/PC/azure-data-portfolio/data/fact_returns.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["return_id", "original_order_id", "return_date", "product_id", "quantity",
                "reason", "refund_amount"])

    reasons = ["Defective", "Wrong Item", "Customer Changed Mind", "Damaged in Shipping", "Quality Issue"]
    return_id = 50000
    for i in range(800):
        order_num = random.randint(10000, order_id - 1)
        pid = random.choice(list(PRODUCTS.keys()))
        product = PRODUCTS[pid]
        qty = random.randint(1, 3)
        ret_date = datetime(2023, 1, 1) + timedelta(days=random.randint(15, 900))
        refund = round(qty * product["unit_price"] * random.uniform(0.8, 1.0), 2)

        w.writerow([
            f"RET-{return_id}", f"ORD-{order_num}", ret_date.strftime("%Y-%m-%d"),
            pid, qty, random.choice(reasons), refund
        ])
        return_id += 1

# --- Generate Targets ---
with open("C:/Users/PC/azure-data-portfolio/data/fact_targets.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["year", "month", "region", "category", "target_revenue", "target_orders"])
    for year in [2023, 2024, 2025]:
        for month in range(1, 13):
            if year == 2025 and month > 6:
                break
            for region in REGIONS:
                for cat in CATEGORIES:
                    base_rev = random.uniform(50000, 300000)
                    growth = 1.0 + (year - 2023) * 0.12
                    target_rev = round(base_rev * growth, 2)
                    target_orders = random.randint(100, 600)
                    w.writerow([year, month, region, cat, target_rev, target_orders])

print("All CSV files generated successfully!")
print(f"Total orders generated: {order_id - 10000}")
print(f"Total products: {len(PRODUCTS)}")
print(f"Total customers: {len(CUSTOMERS)}")
