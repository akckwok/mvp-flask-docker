import argparse
from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the Flask application.")
    parser.add_argument('-t', '--testing', action='store_true', help='Enable testing mode.')
    args = parser.parse_args()

    if args.testing:
        app.config['TESTING'] = True

    app.run(host='0.0.0.0', port=5000, debug=True)
