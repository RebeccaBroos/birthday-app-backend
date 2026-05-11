from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date
import os
import re

app = Flask(__name__)
CORS(app)

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'birthday_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'birthday_password')
DB_NAME = os.getenv('DB_NAME', 'birthday_db')

def get_db_connection():
    """Establish a connection to the PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        return None

def validate_email(email):
    """Validate that email contains @ symbol"""
    if not email or '@' not in email:
        return False, "Email must contain '@' symbol"
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return False, "Email format is invalid"
    return True, ""

def validate_birthdate(birthdate_str):
    """Validate birthdate format (YYYY-MM-DD) and ensure person is 16+ years old"""
    try:
        birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()
    except ValueError:
        return False, "Birthdate must be in format YYYY-MM-DD"
    
    # Check if birthdate is in the past
    if birthdate >= date.today():
        return False, "Birthdate must be in the past"
    
    # Calculate age
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    
    if age < 16:
        return False, f"Must be at least 16 years old (current age: {age})"
    
    return True, ""

def validate_username(username):
    """Validate that username is not empty"""
    if not username or len(username.strip()) == 0:
        return False, "Username cannot be empty"
    if len(username) > 100:
        return False, "Username must be less than 100 characters"
    return True, ""

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Backend service is running'}), 200

@app.route('/submit', methods=['POST'])
def submit_form():
    """Handle form submission from frontend"""
    try:
        data = request.get_json()
        
        # Extract data
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        birthdate = data.get('birthdate', '').strip()
        
        # Validate username
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Validate email
        is_valid, error_msg = validate_email(email)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Validate birthdate
        is_valid, error_msg = validate_birthdate(birthdate)
        if not is_valid:
            return jsonify({'success': False, 'error': error_msg}), 400
        
        # Insert into database
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (email, birthdate) VALUES (%s, %s) RETURNING id;",
                (email, birthdate)
            )
            user_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            
            return jsonify({
                'success': True, 
                'message': f'Successfully registered! User ID: {user_id}',
                'user_id': user_id
            }), 201
            
        except psycopg2.IntegrityError:
            conn.rollback()
            return jsonify({'success': False, 'error': 'Email already registered'}), 400
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Database error: {e}")
            return jsonify({'success': False, 'error': 'Database error occurred'}), 500
        finally:
            conn.close()
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500

@app.route('/users', methods=['GET'])
def get_users():
    """Get all registered users (for testing/debugging)"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, email, birthdate, created_at FROM users ORDER BY created_at DESC;")
        users = cur.fetchall()
        cur.close()
        conn.close()
        
        # Convert date/datetime objects to strings for JSON serialization
        for user in users:
            if isinstance(user['birthdate'], date):
                user['birthdate'] = user['birthdate'].isoformat()
            if isinstance(user['created_at'], datetime):
                user['created_at'] = user['created_at'].isoformat()
        
        return jsonify({'success': True, 'users': users}), 200
    
    except Exception as e:
        print(f"Error fetching users: {e}")
        return jsonify({'success': False, 'error': 'Failed to fetch users'}), 500

if __name__ == '__main__':
    # Run on all interfaces (0.0.0.0) to allow external connections
    app.run(host='0.0.0.0', port=5000, debug=False)
