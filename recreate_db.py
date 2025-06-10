from app import app, db
from models import *

def recreate_database():
    with app.app_context():
        # Xóa tất cả các bảng
        db.drop_all()
        
        # Tạo lại tất cả các bảng
        db.create_all()
        
        # Thêm dữ liệu mẫu (nếu cần)
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('admin123')
        db.session.add(admin)
        
        db.session.commit()
        print("Đã tạo lại cơ sở dữ liệu thành công!")

if __name__ == '__main__':
    recreate_database()
