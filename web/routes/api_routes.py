"""
RESTful API Routes
JSON API endpoints for programmatic access
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api import PassAuditAPI

api_bp = Blueprint('api', __name__)
passaudit_api = PassAuditAPI()


def require_api_key(f):
    """Decorator to require API key (optional, for future use)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For now, API is open. In production, check API key here
        # api_key = request.headers.get('X-API-Key')
        # if not api_key or not validate_api_key(api_key):
        #     return jsonify({'error': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated_function


@api_bp.route('/analyze', methods=['POST'])
@require_api_key
def api_analyze():
    """
    Analyze a single password

    POST /api/v1/analyze
    {
        "password": "string",
        "check_hibp": boolean (optional, default: false)
    }
    """
    try:
        data = request.get_json()

        if not data or 'password' not in data:
            return jsonify({'error': 'Password is required'}), 400

        password = data['password']
        check_hibp = data.get('check_hibp', False)

        if not password:
            return jsonify({'error': 'Password cannot be empty'}), 400

        if len(password) > 128:
            return jsonify({'error': 'Password too long (max 128 characters)'}), 400

        # Analyze password
        result = passaudit_api.analyze_password(password, check_hibp=check_hibp)

        # Remove actual password from response for security
        result.pop('password', None)

        return jsonify({
            'success': True,
            'result': result
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/analyze/batch', methods=['POST'])
@require_api_key
def api_analyze_batch():
    """
    Analyze multiple passwords

    POST /api/v1/analyze/batch
    {
        "passwords": ["string", ...],
        "check_hibp": boolean (optional, default: false)
    }
    """
    try:
        data = request.get_json()

        if not data or 'passwords' not in data:
            return jsonify({'error': 'Passwords array is required'}), 400

        passwords = data['passwords']
        check_hibp = data.get('check_hibp', False)

        if not isinstance(passwords, list):
            return jsonify({'error': 'Passwords must be an array'}), 400

        if not passwords:
            return jsonify({'error': 'Passwords array cannot be empty'}), 400

        if len(passwords) > 1000:
            return jsonify({'error': 'Too many passwords (max 1000)'}), 400

        # Analyze batch
        results = passaudit_api.analyze_batch(passwords, check_hibp=check_hibp)

        # Remove actual passwords from response
        for result in results:
            result.pop('password', None)

        # Calculate summary
        total = len(results)
        avg_score = sum(r['strength_score'] for r in results) / total
        weak_count = sum(1 for r in results if r['strength_score'] < 40)

        return jsonify({
            'success': True,
            'total': total,
            'summary': {
                'average_score': round(avg_score, 1),
                'weak_count': weak_count
            },
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/generate', methods=['POST'])
@require_api_key
def api_generate():
    """
    Generate secure passwords

    POST /api/v1/generate
    {
        "count": integer (optional, default: 1),
        "length": integer (optional, default: 16),
        "use_uppercase": boolean (optional, default: true),
        "use_lowercase": boolean (optional, default: true),
        "use_digits": boolean (optional, default: true),
        "use_symbols": boolean (optional, default: true)
    }
    """
    try:
        data = request.get_json() or {}

        count = data.get('count', 1)
        length = data.get('length', 16)
        use_uppercase = data.get('use_uppercase', True)
        use_lowercase = data.get('use_lowercase', True)
        use_digits = data.get('use_digits', True)
        use_symbols = data.get('use_symbols', True)

        # Validation
        count = min(max(count, 1), 100)
        length = min(max(length, 8), 64)

        if not any([use_uppercase, use_lowercase, use_digits, use_symbols]):
            return jsonify({'error': 'At least one character type must be selected'}), 400

        # Generate passwords
        passwords = passaudit_api.generate_batch(
            count=count,
            length=length,
            use_uppercase=use_uppercase,
            use_lowercase=use_lowercase,
            use_digits=use_digits,
            use_symbols=use_symbols
        )

        return jsonify({
            'success': True,
            'count': len(passwords),
            'passwords': passwords
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/stats', methods=['GET'])
def api_stats():
    """
    Get database statistics

    GET /api/v1/stats
    """
    try:
        stats = {
            'version': '2.0.0',
            'endpoints': {
                'analyze': '/api/v1/analyze',
                'analyze_batch': '/api/v1/analyze/batch',
                'generate': '/api/v1/generate',
                'stats': '/api/v1/stats'
            },
            'limits': {
                'max_password_length': 128,
                'max_batch_size': 1000,
                'max_generate_count': 100
            }
        }

        # Try to get database stats
        try:
            common_passwords_file = os.path.join('data', 'common_passwords.txt')
            if os.path.exists(common_passwords_file):
                with open(common_passwords_file, 'r') as f:
                    count = sum(1 for line in f if line.strip() and not line.startswith('#'))
                stats['database'] = {
                    'common_passwords': count
                }
        except:
            pass

        return jsonify(stats)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
