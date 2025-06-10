from app import app, db
from models import User, Category, Service, Employee, Customer
from datetime import datetime, date

def init_db():
    with app.app_context():
        # Tạo tất cả các bảng
        db.create_all()

        # Kiểm tra xem đã có dữ liệu chưa
        if User.query.first() is None:
            # Tạo user admin
            admin = User(
                username='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)

            # Tạo các danh mục
            categories = [
                Category(name='Cắt tóc', description='Các dịch vụ cắt tóc'),
                Category(name='Nhuộm tóc', description='Các dịch vụ nhuộm tóc'),
                Category(name='Uốn tóc', description='Các dịch vụ uốn tóc'),
                Category(name='Chăm sóc da', description='Các dịch vụ chăm sóc da')
            ]
            db.session.add_all(categories)
            db.session.commit()

            # Tạo các dịch vụ
            services = [
            ]
            db.session.add_all(services)

            # Tạo nhân viên mẫu
            employees = [
                Employee(
                    name='Nguyễn Văn A',
                    phone='0123456789',
                    hire_date=date(2023, 1, 1),
                    salary=8000000
                ),
                Employee(
                    name='Trần Thị B',
                    phone='0987654321',
                    hire_date=date(2023, 2, 1),
                    salary=10000000
                )
            ]
            db.session.add_all(employees)

            # Tạo khách hàng mẫu
            customers = [
                Customer(
                    name='Lê Văn C',
                    phone='0123456788',
                    birth_date=date(1990, 1, 1)
                ),
                Customer(
                    name='Phạm Thị D',
                    phone='0987654322',
                    birth_date=date(1995, 5, 5)
                )
            ]
            db.session.add_all(customers)

            # Lưu tất cả thay đổi
            db.session.commit()
            print("Đã khởi tạo dữ liệu mẫu thành công!")

if __name__ == '__main__':
    init_db() 