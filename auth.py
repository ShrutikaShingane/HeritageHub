from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

# Hum ek Blueprint banayenge taaki app.py clean rahe
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')  # Default user

    if not name or not email or not password:
        return jsonify({'error': 'Please fill all fields'}), 400

    # Password ko hash (encrypt) karein
    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        # Check karein ki email pehle se toh nahi hai
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({'error': 'Email already registered!'}), 400

        # Naya user insert karein
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_password, role)
        )
        conn.commit()
        return jsonify({'message': 'Signup successful! Please login.'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    selected_role = data.get('role')  # User ne dropdown se kya select kiya

    if not email or not password or not selected_role:
        return jsonify({'error': 'Please fill all fields'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor(dictionary=True)

        # User ko dhundhein
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'User not found!'}), 404

        if user['is_blocked']:
            return jsonify({'error': 'Your account is blocked by Admin!'}), 403

        # Password check karein (Plain password vs Hashed password)
        if not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Incorrect password!'}), 401

        # Check karein ki role match ho raha hai ya nahi
        if user['role'] != selected_role:
            return jsonify({'error': f"You are not registered as an {selected_role}!"}), 403

        # Session mein user ki details save karein (Login state)
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['role'] = user['role']

        return jsonify({
            'message': 'Login successful!',
            'role': user['role']
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()