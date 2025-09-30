import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    # Get secret from Doppler (via environment variable)
    secret_message = os.getenv('SECRET_MESSAGE', 'No secret found')

    return jsonify({
        'message': 'Hello, World!',
        'secret': secret_message
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)