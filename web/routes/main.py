"""
Main Routes
Home page, about, and general pages
"""

from flask import Blueprint, render_template, request, jsonify
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api import PassAuditAPI

main_bp = Blueprint('main', __name__)
api = PassAuditAPI()


@main_bp.route('/')
def index():
    """Home page with quick password check"""
    return render_template('index.html')


@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@main_bp.route('/quick-check', methods=['POST'])
def quick_check():
    """Quick password strength check (AJAX endpoint)"""
    try:
        data = request.get_json()
        password = data.get('password', '')

        if not password:
            return jsonify({'error': 'Password is required'}), 400

        if len(password) > 128:
            return jsonify({'error': 'Password too long (max 128 characters)'}), 400

        # Analyze password
        result = api.analyze_password(password, check_hibp=False)

        # Format response
        response = {
            'strength_score': round(result['strength_score'], 1),
            'strength_category': result['strength_category'],
            'length': result['length'],
            'entropy': round(result['entropy'], 2),
            'is_common': result['is_common'],
            'patterns': {
                k: v for k, v in result['patterns'].items() if v
            },
            'feedback': result['feedback'][:3]  # Limit to first 3 suggestions
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
