import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env (chỉ cho local dev)
if os.path.exists('.env'):
    load_dotenv()

class Config:
    # Cấu hình cơ bản
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')

    # Cấu hình database
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
        
    if database_url.startswith('postgresql://'):
        # Thay thế postgresql:// bằng postgresql+psycopg:// để sử dụng driver psycopg
        SQLALCHEMY_DATABASE_URI = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
    else:
        SQLALCHEMY_DATABASE_URI = database_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cấu hình upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Cấu hình phân trang
    ITEMS_PER_PAGE = 10

    # Cấu hình thời gian
    TIMEZONE = 'Asia/Ho_Chi_Minh'