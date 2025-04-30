from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Date
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Manager(Base):
    __tablename__ = "managers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    users = relationship("User", back_populates="manager")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    manager_id = Column(Integer, ForeignKey("managers.id"))
    manager = relationship("Manager", back_populates="users")
    orders = relationship("Order", back_populates="user")
    hr_record = relationship("HRRecord", back_populates="user", uselist=False)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    price = Column(Float)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class HRRecord(Base):
    __tablename__ = "hr_records"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    start_date = Column(Date, nullable=False)
    vacation_days = Column(Integer, default=0)

    user = relationship("User", back_populates="hr_record")