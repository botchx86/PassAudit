"""
PassAudit Web Server
Launch script for the Flask web interface
"""

import argparse
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from web.app import create_app


def main():
    """Main entry point for web server"""
    parser = argparse.ArgumentParser(
        description="PassAudit Web Interface"
    )

    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1)'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to bind to (default: 5000)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Run in debug mode (auto-reload on changes)'
    )

    parser.add_argument(
        '--no-debug',
        action='store_true',
        help='Run in production mode (no debug)'
    )

    args = parser.parse_args()

    # Create Flask app
    app = create_app()

    # Determine debug mode
    debug_mode = args.debug
    if args.no_debug:
        debug_mode = False

    # Print startup information
    print("="*70)
    print("PassAudit Web Interface")
    print("="*70)
    print(f"Server starting on: http://{args.host}:{args.port}")
    print(f"Debug mode: {'Enabled' if debug_mode else 'Disabled'}")
    print()
    print("Press CTRL+C to stop the server")
    print("="*70)
    print()

    # Start server
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=debug_mode
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError starting server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
