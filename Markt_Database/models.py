from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, VARCHAR, TIMESTAMP, BIGINT, DECIMAL, INTEGER, TEXT, BOOLEAN


Base = declarative_base()


class Products(Base):
    """
    Product Database Models
    """

    __tablename__ = "products"

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(200), default=None)
    brand = Column(VARCHAR(200), default=None)
    sku = Column(VARCHAR(200), default=None)
    created_at = Column(TIMESTAMP, default=None)
    measurement_value = Column(DECIMAL(8, 2), default=None)
    measurement = Column(TEXT, default=None)


class ProductsEans(Base):
    """
    Product Eans Database Model
    """

    __tablename__ = "products_eans"

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    id_product = Column(BIGINT)
    ean = Column(BIGINT)


class Stores(Base):
    """
    Store Database Model
    """

    __tablename__ = "stores"

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(200), default=None)


class Prices(Base):
    """
    Price Database Model
    """

    __tablename__ = "prices"

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    id_store = Column(INTEGER)
    id_product = Column(INTEGER)
    price = Column(DECIMAL(8, 2), default=None)
    price_promotion = Column(DECIMAL(8, 2), default=None)
    updated_at = Column(TIMESTAMP, default=None)


class PricesHistory(Base):
    """
    Price Database Model
    """

    __tablename__ = "prices_history"

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    id_store = Column(INTEGER)
    id_product = Column(INTEGER)
    price = Column(DECIMAL(8, 2), default=None)
    price_promotion = Column(DECIMAL(8, 2), default=None)
    created_at = Column(TIMESTAMP, default=None)


class ShoppingLists(Base):
    """
    Shopping List Database Model
    """

    __tablename__ = "shopping_lists"

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    ean = Column(BIGINT)
    user_id = Column(INTEGER)
    exists = Column(BOOLEAN, default=False)
    created_at = Column(TIMESTAMP, default=None)