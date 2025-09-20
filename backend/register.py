from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import bcrypt
import getpass

# --- Initialize the Flask App ---
app = Flask(__name__)
# Enable CORS to allow frontend to make requests
CORS(app) 

# --- Database Connection Function ---
def get_db_connection():
    """Establishes a connection to the MySQL database."""
    # This configuration should ideally be in a separate config file
    return mysql.connector.connect(
        host="localhost",
        user="your_username",  # Replace with your MySQL username
        password="your_password",  # Replace with your MySQL password
        database="paisabuddy"
    )

# --- Password Hashing/Verification Functions ---
def hash_password(password):
    """Hashes the password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(plain_password, hashed_password):
    """Verifies the plain password against the hashed one."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# --- API Endpoint for User Registration ---
@app.route('/register', methods=['POST'])
def register_user():
    """API endpoint to register a new user."""
    # Get data sent from the frontend (in JSON format)
    data = request.get_json()
    name = data.get('name')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([name, username, email, password]):
        return jsonify({"message": "Missing required fields"}), 400

    hashed_password = hash_password(password)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = "INSERT INTO Users (name, username, email, password_hash) VALUES (%s, %s, %s, %s)"
        val = (name, username, email, hashed_password)
        cursor.execute(sql, val)
        conn.commit()
        return jsonify({"message": "Registration successful!"}), 201 # 201 means Created
    except mysql.connector.Error as err:
        conn.rollback()
        # Check for duplicate entry error
        if err.errno == 1062:
            return jsonify({"message": "Username or email already exists."}), 409 # 409 means Conflict
        return jsonify({"message": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

# --- API Endpoint for User Login ---
@app.route('/login', methods=['POST'])
def login_user():
    """API endpoint for a user to log in."""
    data = request.get_json()
    user_identifier = data.get('user_identifier') # Frontend sends username or email
    password = data.get('password')

    if not user_identifier or not password:
        return jsonify({"message": "Missing username/email or password"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) # dictionary=True makes result accessible by column name

    try:
        sql = "SELECT id, name, password_hash FROM Users WHERE username = %s OR email = %s"
        cursor.execute(sql, (user_identifier, user_identifier))
        user_record = cursor.fetchone()

        if user_record and verify_password(password, user_record['password_hash'].encode('utf-8')):
            # Login successful
            return jsonify({
                "message": f"Login successful! Welcome, {user_record['name']}.",
                "user": {
                    "id": user_record['id'],
                    "name": user_record['name']
                }
            }), 200 # 200 means OK
        else:
            # Invalid credentials
            return jsonify({"message": "Invalid credentials. Please try again."}), 401 # 401 means Unauthorized
    except mysql.connector.Error as err:
        return jsonify({"message": f"An error occurred: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

# --- To run the Flask app ---
if __name__ == "__main__":
    # The server will run on http://127.0.0.1:5000
    app.run(debug=True)