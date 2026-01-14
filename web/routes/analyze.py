"""
Analysis Routes
Password analysis endpoints and pages
"""

from flask import Blueprint, render_template, request, jsonify, session
import sys
import os
from werkzeug.utils import secure_filename

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from api import PassAuditAPI

analyze_bp = Blueprint('analyze', __name__)
api = PassAuditAPI()


@analyze_bp.route('/analyze')
def analyze_page():
    """Analysis page"""
    return render_template('analyze.html')


@analyze_bp.route('/analyze/single', methods=['POST'])
def analyze_single():
    """Analyze a single password"""
    try:
        data = request.get_json()
        password = data.get('password', '')
        check_hibp = data.get('check_hibp', False)

        if not password:
            return jsonify({'error': 'Password is required'}), 400

        if len(password) > 128:
            return jsonify({'error': 'Password too long (max 128 characters)'}), 400

        # Analyze password
        result = api.analyze_password(password, check_hibp=check_hibp)

        # Store in session for potential export
        if 'analysis_results' not in session:
            session['analysis_results'] = []

        session['analysis_results'].append(result)
        session.modified = True

        # Format response
        response = {
            'password_masked': '*' * len(password),
            'length': result['length'],
            'strength_score': round(result['strength_score'], 1),
            'strength_category': result['strength_category'],
            'entropy': round(result['entropy'], 2),
            'pool_entropy': round(result['pool_entropy'], 2),
            'is_common': result['is_common'],
            'patterns': result['patterns'],
            'feedback': result['feedback']
        }

        # Add HIBP data if checked
        if check_hibp:
            response['hibp_pwned'] = result.get('hibp_pwned', False)
            response['hibp_count'] = result.get('hibp_count', 0)

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analyze_bp.route('/analyze/batch', methods=['POST'])
def analyze_batch():
    """Analyze multiple passwords from file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Check file extension
        if not file.filename.endswith('.txt'):
            return jsonify({'error': 'Only .txt files are supported'}), 400

        # Read passwords from file
        content = file.read().decode('utf-8')
        passwords = [line.strip() for line in content.splitlines() if line.strip()]

        if not passwords:
            return jsonify({'error': 'No passwords found in file'}), 400

        if len(passwords) > 1000:
            return jsonify({'error': 'Too many passwords (max 1000)'}), 400

        check_hibp = request.form.get('check_hibp', 'false').lower() == 'true'

        # Analyze batch
        results = api.analyze_batch(passwords, check_hibp=check_hibp)

        # Store in session
        session['analysis_results'] = results
        session['batch_analysis'] = True
        session.modified = True

        # Calculate summary statistics
        total = len(results)
        avg_score = sum(r['strength_score'] for r in results) / total
        weak_count = sum(1 for r in results if r['strength_score'] < 40)
        common_count = sum(1 for r in results if r['is_common'])

        strength_dist = {
            'very_weak': sum(1 for r in results if r['strength_score'] < 20),
            'weak': sum(1 for r in results if 20 <= r['strength_score'] < 40),
            'medium': sum(1 for r in results if 40 <= r['strength_score'] < 60),
            'strong': sum(1 for r in results if 60 <= r['strength_score'] < 80),
            'very_strong': sum(1 for r in results if r['strength_score'] >= 80)
        }

        response = {
            'success': True,
            'total': total,
            'summary': {
                'total_passwords': total,
                'average_score': round(avg_score, 1),
                'weak_count': weak_count,
                'common_count': common_count,
                'strength_distribution': strength_dist
            },
            'results': [
                {
                    'password_masked': '*' * len(passwords[i]),
                    'strength_score': round(r['strength_score'], 1),
                    'strength_category': r['strength_category'],
                    'is_common': r['is_common'],
                    'patterns': {k: v for k, v in r['patterns'].items() if v}
                }
                for i, r in enumerate(results[:100])  # Limit to first 100 for display
            ]
        }

        if check_hibp:
            breached_count = sum(1 for r in results if r.get('hibp_pwned', False))
            response['summary']['breached_count'] = breached_count

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analyze_bp.route('/results')
def results_page():
    """Results page showing session analysis results"""
    results = session.get('analysis_results', [])
    batch_analysis = session.get('batch_analysis', False)

    if not results:
        return render_template('results.html', results=None)

    return render_template('results.html', results=results, batch_analysis=batch_analysis)
