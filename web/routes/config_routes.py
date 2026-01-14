"""
Configuration Routes
Configuration viewing and management endpoints
"""

from flask import Blueprint, render_template, request, jsonify
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.config import LoadConfig, UpdateConfigValue
from utils.cache import get_cache

config_bp = Blueprint('config', __name__)


@config_bp.route('/')
def config_page():
    """Configuration page"""
    config = LoadConfig()
    return render_template('config.html', config=config)


@config_bp.route('/view', methods=['GET'])
def view_config():
    """Get current configuration (AJAX)"""
    try:
        config = LoadConfig()
        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@config_bp.route('/cache/stats', methods=['GET'])
def cache_stats():
    """Get HIBP cache statistics"""
    try:
        cache = get_cache()
        stats = cache.get_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@config_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear HIBP cache"""
    try:
        cache = get_cache()
        cache.clear()
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
