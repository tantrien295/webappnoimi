# Khởi Nghiệp Salon - Hệ thống quản lý Salon

Đây là một ứng dụng web được xây dựng bằng Flask để quản lý hoạt động của một salon, bao gồm quản lý khách hàng, nhân viên, dịch vụ, lịch sử dịch vụ và cài đặt ứng dụng.

## Mục lục

1.  [Yêu cầu](#yêu-cầu)
2.  [Cài đặt](#cài-đặt)
3.  [Chạy ứng dụng với Docker Compose](#chạy-ứng-dụng-với-docker-compose)
4.  [Di chuyển cơ sở dữ liệu](#di-chuyển-cơ-sở-dữ-liệu)
5.  [Truy cập ứng dụng](#truy-cập-ứng-dụng)
6.  [Chạy Tailwind CSS](#chạy-tailwind-css)

## Yêu cầu

Để chạy ứng dụng này, bạn cần cài đặt:

*   [Docker](https://www.docker.com/get-started/)
*   [Docker Compose](https://docs.docker.com/compose/install/)

## Cài đặt

1.  **Clone repository:**
    ```bash
    git clone <URL_REPOSITORY_CỦA_BẠN>
    cd webappnoimi
    ```

## Chạy ứng dụng với Docker Compose

Sử dụng Docker Compose để xây dựng và chạy ứng dụng cùng với cơ sở dữ liệu PostgreSQL.

1.  **Xây dựng và khởi động các dịch vụ:**
    ```bash
    docker-compose up --build -d
    ```
    Lệnh này sẽ xây dựng các Docker image (nếu chưa có hoặc có thay đổi), tạo các container và khởi động chúng trong chế độ nền.

## Di chuyển cơ sở dữ liệu

Sau khi các dịch vụ Docker đã chạy, bạn cần khởi tạo và áp dụng các bản di chuyển cơ sở dữ liệu để tạo bảng và cấu hình dữ liệu ban đầu.

1.  **Xóa thư mục migrations cũ (nếu có, đặc biệt khi gặp lỗi database schema)**:
    ```bash
    Remove-Item -Recurse -Force migrations # Đối với PowerShell trên Windows
    # hoặc
    # rm -rf migrations # Đối với Linux/macOS
    ```

2.  **Khởi tạo Flask-Migrate**:
    ```bash
    docker-compose run --rm web flask db init
    ```
    Lệnh này sẽ tạo thư mục `migrations` và các tệp cấu hình cần thiết.

3.  **Tạo bản di chuyển ban đầu**:
    ```bash
    docker-compose run --rm web flask db migrate -m "Initial migration"
    ```
    Lệnh này sẽ quét các mô hình SQLAlchemy của bạn và tạo một bản di chuyển dựa trên các thay đổi schema.

4.  **Áp dụng bản di chuyển vào cơ sở dữ liệu**:
    ```bash
    docker-compose run --rm web flask db upgrade
    ```
    Lệnh này sẽ thực thi bản di chuyển đã tạo, tạo các bảng trong cơ sở dữ liệu PostgreSQL.

5.  **Chạy lại ứng dụng (sau khi di chuyển)**:
    Sau khi di chuyển, bạn nên dừng và khởi động lại các container để đảm bảo ứng dụng kết nối với cơ sở dữ liệu đã được cập nhật.
    ```bash
    docker-compose down
    docker-compose up -d
    ```

## Truy cập ứng dụng

Sau khi các container đã chạy, bạn có thể truy cập ứng dụng tại:

[http://localhost:5000](http://localhost:5000)

## Chạy Tailwind CSS

Nếu bạn thực hiện bất kỳ thay đổi nào đối với các tệp mẫu (`.html`) hoặc cấu hình Tailwind, bạn cần biên dịch lại CSS:

```bash
npx tailwindcss -i ./static/css/main.css -o ./static/css/output.css --minify
```

Bạn cũng có thể chạy Tailwind CSS ở chế độ "watch" để tự động biên dịch khi có thay đổi:

```bash
npx tailwindcss -i ./static/css/main.css -o ./static/css/output.css --watch
```

Chúc bạn thành công! 