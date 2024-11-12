from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, Text, Float, func
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, timezone


user_roles = Enum('customer', 'vendor', 'admin', name='user_roles')

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False)
    role = Column(user_roles, default='customer')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False) 
    description = Column(Text, nullable=True)  
    
class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey('categories.id', nullable=False))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())    
    
    category = relationship('Category', back_populates='products')  # Relación con categorías
    
# Relación de la categoría con los productos
Category.products = relationship('Product', order_by=Product.id, back_populates='category')

class ProductVariant(Base):
    __tablename__ = 'product_variants'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    name = Column(String(100), nullable=False)  # Nombre de la variante (ej. "Color", "Tamaño")
    value = Column(String(100), nullable=False)  # Valor de la variante (ej. "Rojo", "L")

    product = relationship('Product', back_populates='variants')

Product.variants = relationship('ProductVariant', order_by=ProductVariant.id, back_populates='product')

class ProductImage(Base):
    __tablename__ = 'product_images'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    url = Column(String(255), nullable=False)  # URL de la imagen

    product = relationship('Product', back_populates='images')

Product.images = relationship('ProductImage', order_by=ProductImage.id, back_populates='product')

class Discount(Base):
    __tablename__ = 'discounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)  # Código del cupón, debe ser único
    description = Column(Text, nullable=True)  
    discount_type = Column(Enum('percentage', 'fixed', name='discount_types'), nullable=False)  # Tipo de descuento
    value = Column(Float, nullable=False)  # Valor del descuento (porcentaje o cantidad fija)
    start_date = Column(DateTime, nullable=False)  # Fecha de inicio del descuento
    end_date = Column(DateTime, nullable=False)  # Fecha de finalización del descuento
    is_active = Column(Boolean, default=True)  # Descuento activo o no
    max_uses = Column(Integer, nullable=True)  # Máximo número de usos
    times_used = Column(Integer, default=0)  # Veces utilizado

    orders = relationship('Order', back_populates='discount')
    
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Clave foránea hacia usuario
    status = Column(String(50), nullable=False, default='pendiente')  
    total_amount = Column(Float, nullable=False)  
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 

    user = relationship('User', back_populates='orders')
    discount = relationship('Discount', back_populates='orders')  # Relación con descuentos
    items = relationship('OrderItem', order_by='OrderItem.id', back_populates='order')

# Relación del usuario con los pedidos
User.orders = relationship('Order', order_by=Order.id, back_populates='user')

class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)  # Clave foránea hacia pedidos
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)  # Clave foránea hacia productos
    quantity = Column(Integer, nullable=False)  
    price = Column(Float, nullable=False)  
    subtotal = Column(Float, nullable=False)  

    order = relationship('Order', back_populates='items')  # Relación con pedidos
    product = relationship('Product')  # Relación con productos

# Relación del pedido con los ítems
Order.items = relationship('OrderItem', order_by=OrderItem.id, back_populates='order')

class OrderStatus(Base):
    __tablename__ = 'order_statuses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    status = Column(String(50), nullable=False)  
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship('Order', back_populates='status_history')

Order.status_history = relationship('OrderStatus', order_by=OrderStatus.id, back_populates='order')

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    rating = Column(Integer, nullable=False)  
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship('Product', back_populates='reviews')
    user = relationship('User')

Product.reviews = relationship('Review', order_by=Review.id, back_populates='product')