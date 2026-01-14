"""
Generation Routes
Password generation endpoints
"""

from flask import Blueprint, request, jsonify
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api import PassAuditAPI

generate_bp = Blueprint('generate', __name__)
api = PassAuditAPI()


@generate_bp.route('/generate', methods=['POST'])
def generate_passwords():
    """Generate secure passwords"""
    try:
        data = request.get_json()

        count = data.get('count', 1)
        length = data.get('length', 16)
        use_uppercase = data.get('use_uppercase', True)
        use_lowercase = data.get('use_lowercase', True)
        use_digits = data.get('use_digits', True)
        use_symbols = data.get('use_symbols', True)

        # Validation
        count = min(max(count, 1), 100)  # Limit 1-100
        length = min(max(length, 8), 64)  # Limit 8-64

        if not any([use_uppercase, use_lowercase, use_digits, use_symbols]):
            return jsonify({'error': 'At least one character type must be selected'}), 400

        # Generate passwords
        passwords = api.generate_batch(
            count=count,
            length=length,
            use_uppercase=use_uppercase,
            use_lowercase=use_lowercase,
            use_digits=use_digits,
            use_symbols=use_symbols
        )

        # Analyze generated passwords
        results = []
        for password in passwords:
            result = api.analyze_password(password)
            results.append({
                'password': password,
                'strength_score': round(result['strength_score'], 1),
                'strength_category': result['strength_category'],
                'entropy': round(result['entropy'], 2)
            })

        return jsonify({
            'success': True,
            'count': len(passwords),
            'passwords': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
