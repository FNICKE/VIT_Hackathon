from flask import jsonify, request

def login_logic():
    # Get data from React frontend
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Example logic: replace this with database checks
    if email == "test@example.com" and password == "password123":
        return jsonify({"message": "Login successful!", "status": "success"}), 200
    else:
        return jsonify({"message": "Invalid credentials", "status": "error"}), 401

def register_logic():
    data = request.get_json()
    # Add logic to save user to Algorand or a database here
    return jsonify({"message": "User registered successfully!"}), 201