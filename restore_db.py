import os
import subprocess
import sys
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

def restore_backup(backup_file):
    """Khôi phục database từ file backup"""
    if not os.path.exists(backup_file):
        print(f"Backup file not found: {backup_file}")
        return False
    
    try:
        # Khôi phục database sử dụng pg_restore
        subprocess.run([
            'pg_restore',
            f'--dbname=postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@{os.getenv("POSTGRES_HOST")}:{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_DB")}',
            '--clean',  # Xóa database hiện tại trước khi khôi phục
            '--if-exists',  # Không báo lỗi nếu database không tồn tại
            backup_file
        ], check=True)
        
        print(f"Database restored successfully from: {backup_file}")
        return True
        
    except Exception as e:
        print(f"Error restoring database: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python restore_db.py <backup_file>")
        sys.exit(1)
    
    backup_file = sys.argv[1]
    restore_backup(backup_file) 