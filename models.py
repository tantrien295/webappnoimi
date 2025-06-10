from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    birth_date = db.Column(db.Date)
    address = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service_histories = db.relationship('ServiceHistory', backref='customer', lazy=True)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service_histories = db.relationship('ServiceHistory', backref='service', lazy=True)

    def __repr__(self):
        return f"<Service {self.name}>"

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hire_date = db.Column(db.Date, default=datetime.utcnow().date())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    service_histories = db.relationship('ServiceHistory', backref='employee', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # services = db.relationship('Service', backref='category', lazy=True) # Xóa hoặc comment lại dòng này

class ServiceHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    service_date = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    images = db.relationship('ServiceHistoryImage', backref='service_history', lazy=True, cascade='all, delete-orphan')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ServiceHistoryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_history_id = db.Column(db.Integer, db.ForeignKey('service_history.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), default='Khởi Nghiệp Salon')
    company_logo_url = db.Column(db.String(255), default='static/images/default_logo.png') # Default logo path
    primary_color = db.Column(db.String(7), default='#0ea5e9') # Tailwind primary-500
    address = db.Column(db.String(255), default='Địa chỉ Salon của bạn')
    phone = db.Column(db.String(20), default='0123456789')
    email = db.Column(db.String(100), default='contact@khoinghiemsalon.com')
    facebook_url = db.Column(db.String(255))
    instagram_url = db.Column(db.String(255))
    youtube_url = db.Column(db.String(255))
    welcome_title = db.Column(db.String(255), default='Chào mừng đến với Khởi Nghiệp Salon')
    welcome_subtitle = db.Column(db.String(255), default='Hệ thống quản lý salon chuyên nghiệp')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 