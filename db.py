import os
import pymysql
import pymysql.cursors
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME", "online_voting")

def get_db_connection(use_db=True):
    """
    Returns a PyMySQL database connection.
    If use_db is False, connects without selecting a database (useful for creation).
    """
    db = DB_NAME if use_db else None
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=db,
        cursorclass=pymysql.cursors.DictCursor
    )

def init_db():
    """ Initialize the database and all required tables """
    # 1. Connect without selecting a database to create it if it doesn't exist
    conn = get_db_connection(use_db=False)
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    conn.close()

    # 2. Connect to the specified database to create tables
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('voter', 'admin') DEFAULT 'voter',
                has_voted BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Create candidates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            )
        """)

        # Create votes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                candidate_id INT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_vote (user_id)
            )
        """)

        # Insert a default admin account if not exists
        cursor.execute("SELECT id FROM users WHERE email='admin@voting.com'")
        if not cursor.fetchone():
            from werkzeug.security import generate_password_hash
            hashed_pw = generate_password_hash('admin123')
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                ('System Admin', 'admin@voting.com', hashed_pw, 'admin')
            )
            
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    # You can run this directly to test database creation
    init_db()
