from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from models import db, Customer, Service, Employee, Category, ServiceHistory, ServiceHistoryImage, Settings
from config import Config
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from flask_moment import Moment
import uuid
from sqlalchemy import or_, and_

# Import filters
from filters import init_app as init_filters

# Định nghĩa các phần mở rộng cho phép
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Khởi tạo ứng dụng Flask ở cấp cao nhất ---
app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config) # Sử dụng Config class trực tiếp

# Cấu hình UPLOAD_FOLDER động cho môi trường Vercel hoặc cục bộ
if os.environ.get('VERCEL'):
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
    # Thiết lập instance_path cho Vercel
    app.instance_path = '/tmp/instance'
else:
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    # Đảm bảo thư mục upload cục bộ tồn tại
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

# Khởi tạo các phần mở rộng
db.init_app(app)
migrate = Migrate(app, db)

# Khởi tạo Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Khởi tạo Flask-Moment
moment = Moment(app)

# Tạo một user ảo để tương thích với code hiện tại
class DummyUser:
    def __init__(self):
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        self.role = 'admin'
        self.username = 'admin'

    def get_id(self):
        return '1'

@login_manager.user_loader
def load_user(user_id):
    return DummyUser()

# Context processor để cung cấp biến now cho tất cả các template
@app.context_processor
def inject_now_and_datetime():
    return {'now': datetime.now(), 'datetime': datetime}

@app.context_processor
def inject_moment():
    return dict(moment=moment)

# Context processor để cung cấp cài đặt cho tất cả các template
@app.context_processor
def inject_settings():
    settings = Settings.query.first()
    if not settings:
        settings = Settings() # Tạo cài đặt mặc định nếu chưa có
        db.session.add(settings)
        db.session.commit()
    return {'settings': settings}

# Route tĩnh cho thư mục uploads
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    print(f"\n=== DEBUG ===")
    print(f"Requested filename: {filename}")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(f"Full path: {full_path}")
    print(f"File exists: {os.path.exists(full_path)}")

    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        print(f"Error serving {filename}: {str(e)}")
        return str(e), 404

# Tạo một đối tượng user ảo
def get_current_user():
    return DummyUser()

# Đã xóa các route đăng nhập/đăng xuất

# Routes cho trang chủ
@app.route('/')
def index():
    # Không cần đăng nhập
    
    # Lấy thống kê
    total_customers = Customer.query.count()
    total_employees = Employee.query.count()
    total_services = Service.query.count()
    total_service_history = ServiceHistory.query.count()
    
    return render_template('index.html',
                        total_customers=total_customers,
                        total_employees=total_employees,
                        total_services=total_services,
                        total_service_history=total_service_history)

# Routes cho quản lý khách hàng
@app.route('/customers')
def customer_list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    birth_day = request.args.get('birth_day', type=int)
    birth_month = request.args.get('birth_month', type=int)

    query = Customer.query

    if search:
        query = query.filter(or_(
            Customer.name.ilike(f'%{search}%'),
            Customer.phone.ilike(f'%{search}%')
        ))
    
    if birth_month:
        query = query.filter(db.extract('month', Customer.birth_date) == birth_month)
        if birth_day:
            query = query.filter(db.extract('day', Customer.birth_date) == birth_day)

    query = query.order_by(Customer.name.asc())

    pagination = query.paginate(
        page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)

    return render_template('customers/index.html',
                        customers=pagination.items,
                        pagination=pagination,
                        search=search,
                        birth_day=birth_day,
                        birth_month=birth_month)

@app.route('/customers/add', methods=['GET', 'POST'])
def customer_add():
    if request.method == 'POST':
        try:
            # Chỉ lấy các trường còn lại trên form: Họ và tên, Số điện thoại, Ngày sinh, Địa chỉ, Ghi chú
            name = request.form.get('name')
            phone = request.form.get('phone')
            birth_date_str = request.form.get('birth_date')
            address = request.form.get('address')
            notes = request.form.get('notes')

            # Xử lý ngày sinh: dd-mm-yyyy hoặc dd-mm (mặc định năm 1900)
            birth_date = None
            if birth_date_str:
                try:
                    # Thử định dạng dd-mm-yyyy
                    birth_date = datetime.strptime(birth_date_str, '%d-%m-%Y').date()
                except ValueError:
                    try:
                        # Thử định dạng dd-mm và đặt năm 1900
                        birth_date = datetime.strptime(birth_date_str, '%d-%m').date().replace(year=1900)
                    except ValueError:
                        flash('Định dạng ngày sinh không hợp lệ. Vui lòng sử dụng định dạng dd-mm hoặc dd-mm-yyyy.', 'danger')
                        return render_template('customers/add.html'), 400

            # Kiểm tra các trường bắt buộc (Họ và tên, Số điện thoại)
            if not name or not phone:
                 flash('Họ và tên và Số điện thoại là bắt buộc.', 'danger')
                 # Có thể cần truyền lại dữ liệu đã nhập và thông báo lỗi cụ thể hơn
                 return render_template('customers/add.html'), 400

            customer = Customer(
                name=name,
                phone=phone,
                birth_date=birth_date,
                address=address,
                notes=notes,
                # Status sẽ nhận giá trị mặc định từ model (active)
                # email sẽ nhận giá trị mặc định là NULL từ model (vì đã xóa khỏi form và DB)
            )
            db.session.add(customer)
            db.session.commit()
            flash('Thêm khách hàng thành công!', 'success')
            return redirect(url_for('customer_list'))
        except Exception as e:
            db.session.rollback()
            print(f"Error adding customer: {e}") # In lỗi chi tiết hơn để debug
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            # Có thể cần truyền lại dữ liệu đã nhập
            return render_template('customers/add.html'), 400

    return render_template('customers/add.html')

@app.route('/customers/<int:id>/edit', methods=['GET', 'POST'])
def customer_edit(id):
    customer = Customer.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form, sử dụng .get() cho tất cả các trường
            customer.name = request.form.get('name')
            customer.phone = request.form.get('phone')
            birth_date_str = request.form.get('birth_date')
            customer.address = request.form.get('address')
            customer.notes = request.form.get('notes')

            # Xử lý ngày sinh tương tự hàm add
            birth_date = None
            if birth_date_str:
                try:
                    # Thử định dạng dd-mm-yyyy
                    birth_date = datetime.strptime(birth_date_str, '%d-%m-%Y').date()
                except ValueError:
                    try:
                        # Thử định dạng dd-mm và đặt năm 1900
                        birth_date = datetime.strptime(birth_date_str, '%d-%m').date().replace(year=1900)
                    except ValueError:
                        flash('Định dạng ngày sinh không hợp lệ. Vui lòng sử dụng dd-mm hoặc dd-mm-yyyy.', 'danger')
                        # Truyền lại dữ liệu đã nhập và đối tượng customer
                        return render_template('customers/edit.html', customer=customer), 400
            customer.birth_date = birth_date # Cập nhật ngày sinh của đối tượng customer
            
            # Kiểm tra các trường bắt buộc (Họ và tên, Số điện thoại)
            if not customer.name or not customer.phone:
                 flash('Họ và tên và Số điện thoại là bắt buộc.', 'danger')
                 # Có thể cần truyền lại dữ liệu đã nhập và thông báo lỗi cụ thể hơn
                 return render_template('customers/edit.html', customer=customer), 400

            # Status không còn trên form, không cần cập nhật
            # Email không còn trên form, không cần cập nhật

            db.session.commit()
            flash('Cập nhật thông tin khách hàng thành công!', 'success')
            # Chuyển hướng về trang danh sách
            return redirect(url_for('customer_list'))
        except Exception as e:
            db.session.rollback()
            print(f"Error editing customer: {e}") # In lỗi chi tiết hơn để debug
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            # Có thể cần truyền lại dữ liệu đã nhập
            return render_template('customers/edit.html', customer=customer), 400
    
    return render_template('customers/edit.html', customer=customer)

@app.route('/customers/<int:id>/view')
def customer_view(id):
    customer = Customer.query.get_or_404(id)
    
    # Thêm phân trang cho lịch sử dịch vụ
    page = request.args.get('page', 1, type=int)
    pagination = ServiceHistory.query.filter_by(customer_id=id).order_by(ServiceHistory.service_date.desc()).paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'])
    
    return render_template('customers/view.html', 
                         customer=customer, 
                         pagination=pagination)

@app.route('/customers/<int:id>/delete', methods=['POST'])
def customer_delete(id):
    customer = Customer.query.get_or_404(id)
    try:
        db.session.delete(customer)
        db.session.commit()
        flash('Xóa khách hàng thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi xảy ra khi xóa khách hàng: {str(e)}', 'danger')
    return redirect(url_for('customer_list'))

# Routes cho quản lý dịch vụ
@app.route('/services')
def service_list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Service.query
    if search:
        query = query.filter(Service.name.ilike(f'%{search}%'))
    
    query = query.order_by(Service.name.asc()) # Sắp xếp theo tên dịch vụ A-Z
    
    pagination = query.paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'])
    return render_template('services/index.html', 
                         services=pagination.items,
                         pagination=pagination)

@app.route('/services/add', methods=['GET', 'POST'])
def service_add():
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form, sử dụng .get() cho các trường không bắt buộc
            name = request.form.get('name')
            description = request.form.get('description')

            # Kiểm tra các trường bắt buộc (tên dịch vụ)
            if not name:
                flash('Tên dịch vụ là bắt buộc.', 'danger')
                return render_template('services/add.html'), 400

            service = Service(
                name=name,
                description=description
            )
            db.session.add(service)
            db.session.commit()
            flash('Thêm dịch vụ thành công!', 'success')
            return redirect(url_for('service_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            return render_template('services/add.html'), 400

    # Xử lý GET request
    return render_template('services/add.html')

@app.route('/services/<int:id>/view')
def service_view(id):
    service = Service.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    # Lấy lịch sử dịch vụ của dịch vụ này, sắp xếp theo ngày dịch vụ giảm dần
    service_histories_query = ServiceHistory.query.filter_by(service_id=service.id).order_by(ServiceHistory.service_date.desc())
    pagination = service_histories_query.paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'])
    return render_template('services/view.html', 
                         service=service,
                         pagination=pagination)

@app.route('/services/<int:id>/edit', methods=['GET', 'POST'])
def service_edit(id):
    service = Service.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Lấy dữ liệu từ form, sử dụng .get() cho các trường có thể không tồn tại
            service.name = request.form.get('name')
            service.description = request.form.get('description')
            
            # Kiểm tra trường bắt buộc (tên dịch vụ)
            if not service.name:
                flash('Tên dịch vụ là bắt buộc.', 'danger')
                return render_template('services/edit.html', service=service), 400

            db.session.commit()
            flash('Cập nhật dịch vụ thành công!', 'success')
            # Redirect về trang chi tiết dịch vụ hoặc danh sách dịch vụ
            return redirect(url_for('service_list')) # Hoặc 'service_view', id=service.id nếu có trang view
            
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra khi cập nhật dịch vụ: {str(e)}', 'danger')
            return render_template('services/edit.html', service=service), 400

    # Xử lý GET request: hiển thị form chỉnh sửa
    return render_template('services/edit.html', service=service)

@app.route('/services/<int:id>/delete', methods=['POST'])
def service_delete(id):
    service = Service.query.get_or_404(id)
    try:
        db.session.delete(service)
        db.session.commit()
        flash('Xóa dịch vụ thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi xảy ra khi xóa dịch vụ: {str(e)}', 'danger')
    return redirect(url_for('service_list'))

# Routes cho quản lý nhân viên
@app.route('/employees')
def employee_list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Employee.query
    if search:
        query = query.filter(Employee.name.ilike(f'%{search}%'))
    
    pagination = query.paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'])
    return render_template('employees/index.html', 
                         employees=pagination.items,
                         pagination=pagination)

@app.route('/employees/add', methods=['GET', 'POST'])
def employee_add():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            phone = request.form.get('phone')
            hire_date_str = request.form.get('hire_date')
            notes = request.form.get('notes')

            hire_date = None
            if hire_date_str:
                try:
                    hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Định dạng ngày thuê không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD.', 'danger')
                    return render_template('employees/add.html'), 400

            if not name or not phone:
                flash('Họ và tên và Số điện thoại là bắt buộc.', 'danger')
                return render_template('employees/add.html'), 400
            
            employee = Employee(
                name=name,
                phone=phone,
                hire_date=hire_date,
                notes=notes
            )
            db.session.add(employee)
            db.session.commit()
            flash('Thêm nhân viên thành công!', 'success')
            return redirect(url_for('employee_list'))
        except Exception as e:
            db.session.rollback()
            print(f"Error adding employee: {e}")
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            return render_template('employees/add.html'), 400

    return render_template('employees/add.html')

@app.route('/employees/<int:id>/edit', methods=['GET', 'POST'])
def employee_edit(id):
    employee = Employee.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            employee.name = request.form.get('name')
            employee.phone = request.form.get('phone')
            hire_date_str = request.form.get('hire_date')
            employee.notes = request.form.get('notes')

            hire_date = None
            if hire_date_str:
                try:
                    hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Định dạng ngày thuê không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD.', 'danger')
                    return render_template('employees/edit.html', employee=employee), 400
            employee.hire_date = hire_date

            if not employee.name or not employee.phone:
                flash('Họ và tên và Số điện thoại là bắt buộc.', 'danger')
                return render_template('employees/edit.html', employee=employee), 400

            db.session.commit()
            flash('Cập nhật nhân viên thành công!', 'success')
            return redirect(url_for('employee_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            return render_template('employees/edit.html', employee=employee), 400

    return render_template('employees/edit.html', employee=employee)

@app.route('/employees/<int:id>/delete', methods=['POST'])
def employee_delete(id):
    employee = Employee.query.get_or_404(id)
    try:
        db.session.delete(employee)
        db.session.commit()
        flash('Xóa nhân viên thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi xảy ra khi xóa nhân viên: {str(e)}', 'danger')
    return redirect(url_for('employee_list'))

@app.route('/employees/<int:id>/view')
def employee_view(id):
    employee = Employee.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    # Lấy lịch sử dịch vụ của nhân viên, sắp xếp theo ngày dịch vụ giảm dần
    service_histories_query = ServiceHistory.query.filter_by(employee_id=employee.id).order_by(ServiceHistory.service_date.desc())
    service_histories_pagination = service_histories_query.paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'])
    return render_template('employees/view.html', 
                           employee=employee,
                           service_histories_pagination=service_histories_pagination)

# Routes cho quản lý danh mục
@app.route('/categories')
def category_list():
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template('categories/index.html', categories=categories)

@app.route('/categories/add', methods=['GET', 'POST'])
def category_add():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            if not name:
                flash('Tên danh mục là bắt buộc.', 'danger')
                return render_template('categories/add.html'), 400
            category = Category(name=name, description=description)
            db.session.add(category)
            db.session.commit()
            flash('Thêm danh mục thành công!', 'success')
            return redirect(url_for('category_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            return render_template('categories/add.html'), 400
    return render_template('categories/add.html')

@app.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
def category_edit(id):
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        try:
            category.name = request.form.get('name')
            category.description = request.form.get('description')
            if not category.name:
                flash('Tên danh mục là bắt buộc.', 'danger')
                return render_template('categories/edit.html', category=category), 400
            db.session.commit()
            flash('Cập nhật danh mục thành công!', 'success')
            return redirect(url_for('category_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            return render_template('categories/edit.html', category=category), 400
    return render_template('categories/edit.html', category=category)

@app.route('/categories/<int:id>/delete', methods=['POST'])
def category_delete(id):
    category = Category.query.get_or_404(id)
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Xóa danh mục thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi xảy ra khi xóa danh mục: {str(e)}', 'danger')
    return redirect(url_for('category_list'))

# Routes cho quản lý lịch sử dịch vụ
@app.route('/service-histories')
def service_history_list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    customer_id = request.args.get('customer_id', type=int)
    employee_id = request.args.get('employee_id', type=int)
    service_id = request.args.get('service_id', type=int)
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    query = ServiceHistory.query.join(Customer).join(Service).join(Employee)

    if search:
        query = query.filter(or_(
            Customer.name.ilike(f'%{search}%'),
            Service.name.ilike(f'%{search}%'),
            Employee.name.ilike(f'%{search}%')
        ))
    if customer_id:
        query = query.filter(ServiceHistory.customer_id == customer_id)
    if employee_id:
        query = query.filter(ServiceHistory.employee_id == employee_id)
    if service_id:
        query = query.filter(ServiceHistory.service_id == service_id)
    
    # Lọc theo khoảng ngày
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        query = query.filter(ServiceHistory.service_date >= start_date)
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        query = query.filter(ServiceHistory.service_date <= end_date)

    query = query.order_by(ServiceHistory.service_date.desc())

    pagination = query.paginate(
        page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
    
    customers = Customer.query.order_by(Customer.name.asc()).all()
    employees = Employee.query.order_by(Employee.name.asc()).all()
    services = Service.query.order_by(Service.name.asc()).all()

    return render_template('service_histories/index.html',
                        service_histories=pagination.items,
                        pagination=pagination,
                        search=search,
                        customer_id=customer_id,
                        employee_id=employee_id,
                        service_id=service_id,
                        start_date=start_date_str,
                        end_date=end_date_str,
                        customers=customers,
                        employees=employees,
                        services=services)

@app.route('/service-histories/add', methods=['GET', 'POST'])
@app.route('/service-histories/add/<int:customer_id>', methods=['GET', 'POST'])
def service_history_add(customer_id=None):
    # customer_id có thể được truyền từ trang chi tiết khách hàng
    customers = Customer.query.order_by(Customer.name.asc()).all()
    employees = Employee.query.order_by(Employee.name.asc()).all()
    services = Service.query.order_by(Service.name.asc()).all()

    if request.method == 'POST':
        try:
            customer_id = request.form.get('customer_id', type=int)
            service_id = request.form.get('service_id', type=int)
            employee_id = request.form.get('employee_id', type=int)
            service_date_str = request.form.get('service_date')
            price = request.form.get('price', type=float)
            payment_method = request.form.get('payment_method')
            notes = request.form.get('notes')
            image_files = request.files.getlist('images')

            # Kiểm tra các trường bắt buộc
            if not all([customer_id, service_id, employee_id, service_date_str, price, payment_method]):
                flash('Vui lòng điền đầy đủ các trường bắt buộc.', 'danger')
                return render_template('service_histories/add.html', customers=customers, employees=employees, services=services, selected_customer_id=customer_id), 400

            service_date = datetime.strptime(service_date_str, '%Y-%m-%dT%H:%M') # Expecting datetime-local format

            service_history = ServiceHistory(
                customer_id=customer_id,
                service_id=service_id,
                employee_id=employee_id,
                service_date=service_date,
                price=price,
                payment_method=payment_method,
                notes=notes
            )
            db.session.add(service_history)
            db.session.commit() # Commit để có service_history.id

            # Xử lý upload ảnh
            for file in image_files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = str(uuid.uuid4()) + '_' + filename
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(filepath)
                    # Lưu đường dẫn tương đối để dễ dàng phục vụ tĩnh
                    image = ServiceHistoryImage(service_history_id=service_history.id, image_url=os.path.join('uploads', unique_filename))
                    db.session.add(image)

            db.session.commit()
            flash('Thêm lịch sử dịch vụ thành công!', 'success')
            return redirect(url_for('service_history_list'))
        except Exception as e:
            db.session.rollback()
            print(f"Error adding service history: {e}")
            flash(f'Có lỗi xảy ra khi thêm lịch sử dịch vụ: {str(e)}', 'danger')
            return render_template('service_histories/add.html', customers=customers, employees=employees, services=services, selected_customer_id=customer_id), 400
    
    return render_template('service_histories/add.html', customers=customers, employees=employees, services=services, selected_customer_id=customer_id)

@app.route('/service-histories/<int:id>/edit', methods=['GET', 'POST'])
def service_history_edit(id):
    service_history = ServiceHistory.query.get_or_404(id)
    customers = Customer.query.order_by(Customer.name.asc()).all()
    employees = Employee.query.order_by(Employee.name.asc()).all()
    services = Service.query.order_by(Service.name.asc()).all()

    if request.method == 'POST':
        try:
            service_history.customer_id = request.form.get('customer_id', type=int)
            service_history.service_id = request.form.get('service_id', type=int)
            service_history.employee_id = request.form.get('employee_id', type=int)
            service_date_str = request.form.get('service_date')
            service_history.price = request.form.get('price', type=float)
            service_history.payment_method = request.form.get('payment_method')
            service_history.notes = request.form.get('notes')

            service_history.service_date = datetime.strptime(service_date_str, '%Y-%m-%dT%H:%M') # Expecting datetime-local format

            db.session.commit()
            flash('Cập nhật lịch sử dịch vụ thành công!', 'success')
            return redirect(url_for('service_history_details', id=service_history.id))
        except Exception as e:
            db.session.rollback()
            print(f"Error updating service history: {e}")
            flash(f'Có lỗi xảy ra khi cập nhật lịch sử dịch vụ: {str(e)}', 'danger')
            return render_template('service_histories/edit.html', service_history=service_history, customers=customers, employees=employees, services=services), 400
    
    return render_template('service_histories/edit.html', service_history=service_history, customers=customers, employees=employees, services=services)

@app.route('/service-histories/<int:id>/upload-images', methods=['POST'])
def upload_service_history_images(id):
    service_history = ServiceHistory.query.get_or_404(id)
    if request.method == 'POST':
        try:
            image_files = request.files.getlist('images')
            if not image_files:
                flash('Vui lòng chọn ít nhất một ảnh để tải lên.', 'danger')
                return redirect(url_for('service_history_details', id=id))

            for file in image_files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    unique_filename = str(uuid.uuid4()) + '_' + filename
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(filepath)
                    image = ServiceHistoryImage(service_history_id=id, image_url=os.path.join('uploads', unique_filename))
                    db.session.add(image)

            db.session.commit()
            flash('Ảnh đã được tải lên thành công!', 'success')
        except Exception as e:
            db.session.rollback()
            print(f"Error uploading images: {e}")
            flash(f'Có lỗi xảy ra khi tải ảnh lên: {str(e)}', 'danger')
    return redirect(url_for('service_history_details', id=id))

@app.route('/service-histories/<int:id>/replace-image/<int:image_id>', methods=['POST'])
def replace_service_history_image(id, image_id):
    service_history = ServiceHistory.query.get_or_404(id)
    image_to_replace = ServiceHistoryImage.query.get_or_404(image_id)

    if request.method == 'POST':
        try:
            new_image_file = request.files.get('new_image')
            if new_image_file and allowed_file(new_image_file.filename):
                # Xóa ảnh cũ nếu tồn tại
                old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(image_to_replace.image_url))
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)

                # Lưu ảnh mới
                filename = secure_filename(new_image_file.filename)
                unique_filename = str(uuid.uuid4()) + '_' + filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                new_image_file.save(filepath)
                image_to_replace.image_url = os.path.join('uploads', unique_filename)
                db.session.commit()
                flash('Ảnh đã được thay thế thành công!', 'success')
            else:
                flash('Vui lòng chọn một file ảnh hợp lệ.', 'danger')
        except Exception as e:
            db.session.rollback()
            print(f"Error replacing image: {e}")
            flash(f'Có lỗi xảy ra khi thay thế ảnh: {str(e)}', 'danger')
    return redirect(url_for('service_history_details', id=id))

@app.route('/service-histories/<int:id>/images/<int:image_id>', methods=['DELETE'])
def delete_service_history_image(id, image_id):
    image_to_delete = ServiceHistoryImage.query.get_or_404(image_id)
    if image_to_delete.service_history_id != id:
        flash('Ảnh không thuộc lịch sử dịch vụ này.', 'danger')
        return redirect(url_for('service_history_details', id=id)), 403

    try:
        # Xóa file ảnh vật lý
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(image_to_delete.image_url))
        if os.path.exists(filepath):
            os.remove(filepath)
        
        db.session.delete(image_to_delete)
        db.session.commit()
        flash('Ảnh đã được xóa thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting image: {e}")
        flash(f'Có lỗi xảy ra khi xóa ảnh: {str(e)}', 'danger')
    return redirect(url_for('service_history_list'))

@app.route('/service-histories/<int:id>/details')
def service_history_details(id):
    service_history = ServiceHistory.query.get_or_404(id)
    return render_template('service_histories/details.html', service_history=service_history)

@app.route('/service-histories/<int:id>/export-pdf')
def export_service_history_pdf(id):
    # Lấy thông tin lịch sử dịch vụ
    service_history = ServiceHistory.query.get_or_404(id)

    # Render template HTML thành chuỗi
    rendered_html = render_template('service_histories/pdf_template.html', service_history=service_history)

    # Tạo PDF từ HTML (sử dụng thư viện xhtml2pdf hoặc tương tự)
    # Đây chỉ là placeholder, bạn cần cài đặt và cấu hình thư viện PDF generator phù hợp
    # Ví dụ với xhtml2pdf:
    # from xhtml2pdf import pisa
    # result_file = BytesIO()
    # pisa_status = pisa.CreatePDF(
    #     rendered_html,                # the HTML to convert
    #     dest=result_file)             # file handle to receive result
    # if pisa_status.err:
    #     return "Lỗi tạo PDF", 500
    # result_file.seek(0)
    # return send_file(result_file, mimetype='application/pdf', as_attachment=True, download_name=f'lich_su_dich_vu_{id}.pdf')

    flash('Tính năng xuất PDF chưa được triển khai. Vui lòng liên hệ nhà phát triển.', 'info')
    return redirect(url_for('service_history_details', id=id))

# Routes cho báo cáo doanh thu
@app.route('/revenue')
def revenue():
    # Lấy thống kê doanh thu
    total_revenue = db.session.query(db.func.sum(ServiceHistory.price)).scalar() or 0

    # Doanh thu theo tháng
    monthly_revenue = db.session.query(
        db.func.strftime('%Y-%m', ServiceHistory.service_date).label('month'),
        db.func.sum(ServiceHistory.price).label('total')
    ).group_by('month').order_by('month').all()

    # Doanh thu theo dịch vụ
    service_revenue = db.session.query(
        Service.name,
        db.func.sum(ServiceHistory.price).label('total')
    ).join(Service).group_by(Service.name).order_by(Service.name).all()

    # Doanh thu theo nhân viên
    employee_revenue = db.session.query(
        Employee.name,
        db.func.sum(ServiceHistory.price).label('total')
    ).join(Employee).group_by(Employee.name).order_by(Employee.name).all()

    return render_template('revenue/index.html',
                        total_revenue=total_revenue,
                        monthly_revenue=monthly_revenue,
                        service_revenue=service_revenue,
                        employee_revenue=employee_revenue)

# Route tĩnh cho thư mục uploads (nếu cần, nhưng Vercel sẽ tự động phục vụ static folder)
@app.route('/static/uploads/<path:filename>')
def serve_uploaded_file(filename):
    # Flask sẽ tìm kiếm trong app.static_folder, nên không cần route này nếu UPLOAD_FOLDER nằm trong static
    # Tuy nhiên, nếu UPLOAD_FOLDER là /tmp/uploads, thì cần route này để phục vụ ảnh
    # Đảm bảo đường dẫn này khớp với image_url lưu trong DB (chỉ là 'uploads/...')
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/test_image')
def test_image():
    # Dùng để kiểm tra việc phục vụ ảnh tĩnh
    # Tạo một file ảnh tạm thời để kiểm tra
    test_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'test_image.png')
    if not os.path.exists(test_image_path):
        from PIL import Image
        img = Image.new('RGB', (60, 30), color = 'red')
        img.save(test_image_path)

    return f'Test image created at {test_image_path}. Try accessing it at /uploads/test_image.png'

@app.route('/service-histories/<int:id>/delete', methods=['POST'])
def service_history_delete(id):
    service_history = ServiceHistory.query.get_or_404(id)
    try:
        # Xóa tất cả các ảnh liên quan
        for image in service_history.images:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(image.image_url))
            if os.path.exists(filepath):
                os.remove(filepath)
            db.session.delete(image)

        db.session.delete(service_history)
        db.session.commit()
        flash('Xóa lịch sử dịch vụ thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Không thể xóa lịch sử dịch vụ: {e}', 'danger')
    return redirect(url_for('service_history_list'))

@app.route('/settings', methods=['GET', 'POST'])
def settings_page():
    settings = Settings.query.first()
    if not settings:
        settings = Settings() # Tạo cài đặt mặc định nếu chưa có
        db.session.add(settings)
        db.session.commit()

    if request.method == 'POST':
        settings.company_name = request.form.get('company_name', '')
        settings.primary_color = request.form.get('primary_color', '')
        settings.address = request.form.get('address', '')
        settings.phone = request.form.get('phone', '')
        settings.email = request.form.get('email', '')
        settings.facebook_url = request.form.get('facebook_url', '')
        settings.instagram_url = request.form.get('instagram_url', '')
        settings.youtube_url = request.form.get('youtube_url', '')
        settings.welcome_title = request.form.get('welcome_title', '')
        settings.welcome_subtitle = request.form.get('welcome_subtitle', '')

        # Xử lý logo upload
        logo_file = request.files.get('company_logo')
        if logo_file and allowed_file(logo_file.filename):
            filename = secure_filename(logo_file.filename)
            unique_filename = str(uuid.uuid4()) + '_' + filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            logo_file.save(filepath)
            settings.company_logo_url = os.path.join('uploads', unique_filename)
        
        db.session.commit()
        flash('Cài đặt đã được cập nhật thành công!', 'success')
        return redirect(url_for('settings_page'))

    return render_template('settings/index.html', settings=settings)

if __name__ == '__main__':
    app.run(debug=True)

# Để Flask CLI có thể tìm thấy app trong quá trình phát triển
# Trong môi trường Vercel, wsgi.py sẽ gọi create_app() trực tiếp
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
