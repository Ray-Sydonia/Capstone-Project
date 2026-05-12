from flask import Blueprint, jsonify
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/health')
def health():
    return jsonify({'status': 'ok'})