import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env (chỉ cho local dev, Vercel sử dụng biến môi trường trực tiếp)
load_dotenv()

class Config:
    # Cấu hình cơ bản
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')

    # Cấu hình database - Luôn sử dụng DATABASE_URL từ biến môi trường
    # VERCEL sẽ tự động cung cấp DATABASE_URL mà chúng ta đã cấu hình
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Cấu hình upload - UPLOAD_FOLDER sẽ được quản lý trong app.py
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Cấu hình phân trang
    ITEMS_PER_PAGE = 10

    # Cấu hình thời gian
    TIMEZONE = 'Asia/Ho_Chi_Minh'