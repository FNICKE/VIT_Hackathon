from flask import Blueprint
from controllers.auth_controller import login_logic, register_logic

# Create a Blueprint (a way to organize routes)
auth_bp = Blueprint('auth_bp', __name__)

# Map the URLs to the controller functions
auth_bp.route('/login', methods=['POST'])(login_logic)
auth_bp.route('/register', methods=['POST'])(register_logic)