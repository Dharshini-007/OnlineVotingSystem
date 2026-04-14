import os
import pymysql
import pymysql.cursors
from dotenv import load_dotenv

# Load environment variables (works locally, ignored in Render)
load_dotenv()

# Get DB credentials from environment variables
DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")
DB_PORT = int(os.environ.get("DB_PORT", 3306))


def get_db_connection():
    """Create and return a database connection"""
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor
    )


def init_db():
    """Initialize tables in the existing Railway database"""

    conn = get_db_connection()
    with conn.cursor() as cursor:

        # USERS TABLE
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

        # CANDIDATES TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            )
        """)

        # VOTES TABLE
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

        # DEFAULT ADMIN
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
