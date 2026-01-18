"""Script to drop and recreate the MySQL database."""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection settings
DB_NAME = os.environ.get('DB_NAME', 'smart_store')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', '3306'))

try:
    # Connect to MySQL server (not to a specific database)
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        charset='utf8mb4'
    )
    
    with connection.cursor() as cursor:
        print(f"Dropping database '{DB_NAME}' if it exists...")
        cursor.execute(f"DROP DATABASE IF EXISTS `{DB_NAME}`")
        
        print(f"Creating database '{DB_NAME}'...")
        cursor.execute(f"CREATE DATABASE `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
    connection.close()
    print(f"\n✓ Database '{DB_NAME}' has been reset successfully!")
    print("\nNow run: py manage.py migrate")
    
except pymysql.err.OperationalError as e:
    print(f"Error: Could not connect to MySQL server.")
    print(f"Details: {e}")
    print(f"\nPlease check:")
    print(f"  - MySQL server is running")
    print(f"  - Username: {DB_USER}")
    print(f"  - Password: {'(set)' if DB_PASSWORD else '(empty)'}")
    print(f"  - Host: {DB_HOST}")
    print(f"  - Port: {DB_PORT}")
except Exception as e:
    print(f"An error occurred: {e}")
