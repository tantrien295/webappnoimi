import os
import subprocess
from datetime import datetime
import schedule
import time
import boto3
from dateutil.relativedelta import relativedelta
import shutil
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

# Cấu hình
BACKUP_DIR = 'backups'
DB_NAME = os.getenv('POSTGRES_DB', 'salon')
DB_USER = os.getenv('POSTGRES_USER', 'postgres')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
RETENTION_DAYS = 30  # Số ngày giữ backup

# Tạo thư mục backup nếu chưa tồn tại
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

def create_backup():
    """Tạo backup database"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"{BACKUP_DIR}/{DB_NAME}_{timestamp}.sql"
    
    try:
        # Tạo backup sử dụng pg_dump
        subprocess.run([
            'pg_dump',
            f'--dbname=postgresql://{DB_USER}:{os.getenv("POSTGRES_PASSWORD")}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
            f'--file={backup_file}',
            '--format=custom',
            '--compress=9'
        ], check=True)
        
        print(f"Backup created successfully: {backup_file}")
        
        # Nén file backup
        compressed_file = f"{backup_file}.gz"
        with open(backup_file, 'rb') as f_in:
            with open(compressed_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Xóa file backup gốc
        os.remove(backup_file)
        
        # Upload lên S3 nếu có cấu hình AWS
        if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
            s3 = boto3.client('s3')
            bucket_name = os.getenv('AWS_BACKUP_BUCKET')
            s3.upload_file(compressed_file, bucket_name, f"database_backups/{os.path.basename(compressed_file)}")
            print(f"Backup uploaded to S3: {compressed_file}")
        
        # Xóa các backup cũ
        cleanup_old_backups()
        
    except Exception as e:
        print(f"Error creating backup: {str(e)}")

def cleanup_old_backups():
    """Xóa các backup cũ hơn RETENTION_DAYS ngày"""
    cutoff_date = datetime.now() - relativedelta(days=RETENTION_DAYS)
    
    for filename in os.listdir(BACKUP_DIR):
        if filename.endswith('.gz'):
            file_path = os.path.join(BACKUP_DIR, filename)
            file_date = datetime.fromtimestamp(os.path.getctime(file_path))
            
            if file_date < cutoff_date:
                os.remove(file_path)
                print(f"Deleted old backup: {filename}")

def schedule_backups():
    """Lên lịch backup hàng ngày"""
    schedule.every().day.at("02:00").do(create_backup)  # Backup lúc 2 giờ sáng
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    print("Starting database backup scheduler...")
    schedule_backups() 