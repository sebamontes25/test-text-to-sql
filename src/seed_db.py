from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import Base, Manager, User, Product, Order, OrderItem
from random import randint, choice, sample
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

# Reset DB
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


Base.metadata.create_all(engine)

with Session(engine) as session:
    # Managers
    managers = [
        Manager(name="Manager A"),
        Manager(name="Manager B"),
        Manager(name="Manager C"),
    ]

    # Users
    user_names = ["Nico", "Luna", "Mateo", "Sara", "Diego", "Eva", "Leo"]
    users = [
        User(
            name=name,
            email=f"{name.lower()}@example.com"
        ) for name in user_names
    ]

    # Assign users to managers
    users[0].manager = managers[0]  # 1 user
    for i in range(1, 4):           # 3 users
        users[i].manager = managers[1]
    for i in range(4, len(users)):  # remaining users
        users[i].manager = managers[2]

    # Products
    product_names = [
        "Phone", "Laptop", "Headphones", "Keyboard", "Mouse",
        "Monitor", "Camera", "Charger", "Tablet", "Speaker"
    ]
    products = [Product(name=name, price=randint(50, 1500))
                for name in product_names]

    # Orders
    orders = []
    for _ in range(20):  # 20 orders total
        user = choice(users)
        order = Order(user=user, created_at=datetime.now(timezone.utc) -
                      timedelta(days=randint(0, 30)))
        num_items = randint(1, 3)
        items = sample(products, num_items)
        for item in items:
            order_item = OrderItem(
                product=item,
                quantity=randint(1, 5),
                price=item.price
            )
            order.items.append(order_item)
        orders.append(order)

    # Commit all
    session.add_all(managers + users + products + orders)
    session.commit()
